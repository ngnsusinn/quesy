from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import (
    Grade, Subject, ContentStrand, Topic, Lesson, LearningOutcome, ProblemArchetype
)

router = APIRouter(prefix="/api/v1/taxonomy", tags=["Taxonomy"])


# ==========================================
# PYDANTIC SCHEMAS (Circular 32/2018/TT-BGDĐT)
# Strictly NO textbook edition field
# ==========================================

class GradeCreate(BaseModel):
    code: str
    name: str
    order_index: int = 0


class GradeOut(BaseModel):
    id: str
    code: str
    name: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class SubjectCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0


class SubjectOut(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class StrandCreate(BaseModel):
    subject_id: str
    grade_id: str
    code: str
    name: str
    order_index: int = 0


class StrandOut(BaseModel):
    id: str
    subject_id: str
    grade_id: str
    code: str
    name: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class TopicCreate(BaseModel):
    strand_id: str
    code: str
    name: str
    order_index: int = 0


class TopicOut(BaseModel):
    id: str
    strand_id: str
    code: str
    name: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class LessonCreate(BaseModel):
    topic_id: str
    code: str
    name: str
    order_index: int = 0


class LessonOut(BaseModel):
    id: str
    topic_id: str
    code: str
    name: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class LearningOutcomeCreate(BaseModel):
    lesson_id: str
    code: str
    description: str
    cognitive_level: str = "RECOGNITION"
    order_index: int = 0


class LearningOutcomeOut(BaseModel):
    id: str
    lesson_id: str
    code: str
    description: str
    cognitive_level: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class ProblemArchetypeCreate(BaseModel):
    learning_outcome_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0


class ProblemArchetypeOut(BaseModel):
    id: str
    learning_outcome_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 6-TIER TREE HIERARCHY SCHEMAS
# ==========================================

class TreeArchetype(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int


class TreeLearningOutcome(BaseModel):
    id: str
    code: str
    description: str
    cognitive_level: str
    order_index: int
    archetypes: List[TreeArchetype] = []


class TreeLesson(BaseModel):
    id: str
    code: str
    name: str
    order_index: int
    learning_outcomes: List[TreeLearningOutcome] = []


class TreeTopic(BaseModel):
    id: str
    code: str
    name: str
    order_index: int
    lessons: List[TreeLesson] = []


class TreeStrand(BaseModel):
    id: str
    code: str
    name: str
    order_index: int
    topics: List[TreeTopic] = []


class TaxonomyTreeResponse(BaseModel):
    subject_id: str
    subject_name: str
    grade_id: str
    grade_name: str
    strands: List[TreeStrand] = []


# ==========================================
# ENDPOINTS
# ==========================================

@router.get("/grades", response_model=List[GradeOut])
def list_grades(db: Session = Depends(get_db)):
    return db.query(Grade).order_by(Grade.order_index).all()


@router.post("/grades", response_model=GradeOut, status_code=status.HTTP_201_CREATED)
def create_grade(payload: GradeCreate, db: Session = Depends(get_db)):
    existing = db.query(Grade).filter(Grade.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Grade code already exists")
    grade = Grade(**payload.dict())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).order_by(Subject.order_index).all()


@router.post("/subjects", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    existing = db.query(Subject).filter(Subject.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject code already exists")
    subj = Subject(**payload.dict())
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return subj


@router.get("/strands", response_model=List[StrandOut])
def list_strands(
    subject_id: Optional[str] = None,
    grade_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ContentStrand)
    if subject_id:
        query = query.filter(ContentStrand.subject_id == subject_id)
    if grade_id:
        query = query.filter(ContentStrand.grade_id == grade_id)
    return query.order_by(ContentStrand.order_index).all()


@router.post("/strands", response_model=StrandOut, status_code=status.HTTP_201_CREATED)
def create_strand(payload: StrandCreate, db: Session = Depends(get_db)):
    strand = ContentStrand(**payload.dict())
    db.add(strand)
    db.commit()
    db.refresh(strand)
    return strand


@router.get("/topics", response_model=List[TopicOut])
def list_topics(
    strand_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Topic)
    if strand_id:
        query = query.filter(Topic.strand_id == strand_id)
    return query.order_by(Topic.order_index).all()


@router.post("/topics", response_model=TopicOut, status_code=status.HTTP_201_CREATED)
def create_topic(payload: TopicCreate, db: Session = Depends(get_db)):
    topic = Topic(**payload.dict())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/lessons", response_model=List[LessonOut])
def list_lessons(
    topic_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Lesson)
    if topic_id:
        query = query.filter(Lesson.topic_id == topic_id)
    return query.order_by(Lesson.order_index).all()


@router.post("/lessons", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
def create_lesson(payload: LessonCreate, db: Session = Depends(get_db)):
    lesson = Lesson(**payload.dict())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.get("/learning-outcomes", response_model=List[LearningOutcomeOut])
def list_learning_outcomes(
    lesson_id: Optional[str] = None,
    cognitive_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LearningOutcome)
    if lesson_id:
        query = query.filter(LearningOutcome.lesson_id == lesson_id)
    if cognitive_level:
        query = query.filter(LearningOutcome.cognitive_level == cognitive_level)
    return query.order_by(LearningOutcome.order_index).all()


@router.post("/learning-outcomes", response_model=LearningOutcomeOut, status_code=status.HTTP_201_CREATED)
def create_learning_outcome(payload: LearningOutcomeCreate, db: Session = Depends(get_db)):
    existing = db.query(LearningOutcome).filter(LearningOutcome.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Learning outcome code already exists")
    lo = LearningOutcome(**payload.dict())
    db.add(lo)
    db.commit()
    db.refresh(lo)
    return lo


@router.get("/problem-archetypes", response_model=List[ProblemArchetypeOut])
def list_problem_archetypes(
    learning_outcome_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ProblemArchetype)
    if learning_outcome_id:
        query = query.filter(ProblemArchetype.learning_outcome_id == learning_outcome_id)
    return query.order_by(ProblemArchetype.order_index).all()


@router.post("/problem-archetypes", response_model=ProblemArchetypeOut, status_code=status.HTTP_201_CREATED)
def create_problem_archetype(payload: ProblemArchetypeCreate, db: Session = Depends(get_db)):
    arch = ProblemArchetype(**payload.dict())
    db.add(arch)
    db.commit()
    db.refresh(arch)
    return arch


# ==========================================
# 6-TIER COMPLETE TAXONOMY TREE ENDPOINT
# GET /api/v1/taxonomy/tree?subject_id=...&grade_id=...
# ==========================================

@router.get("/tree", response_model=TaxonomyTreeResponse)
def get_taxonomy_tree(
    subject_id: Optional[str] = Query(None),
    grade_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns the complete 6-level taxonomy hierarchy according to Circular 32/2018/TT-BGDĐT:
    Subject & Grade -> Strands -> Topics -> Lessons -> LearningOutcomes (YCCĐ) -> ProblemArchetypes.
    """
    # If not provided, default to first subject and grade
    if not subject_id:
        subj = db.query(Subject).filter(Subject.code == "TOAN").first() or db.query(Subject).first()
        if not subj:
            raise HTTPException(status_code=404, detail="No subjects found in database")
        subject_id = subj.id
    else:
        subj = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subj:
            raise HTTPException(status_code=404, detail="Subject not found")

    if not grade_id:
        grd = db.query(Grade).filter(Grade.code == "GRADE_12").first() or db.query(Grade).first()
        if not grd:
            raise HTTPException(status_code=404, detail="No grades found in database")
        grade_id = grd.id
    else:
        grd = db.query(Grade).filter(Grade.id == grade_id).first()
        if not grd:
            raise HTTPException(status_code=404, detail="Grade not found")

    # Fetch strands for this subject and grade
    strands = db.query(ContentStrand).filter(
        ContentStrand.subject_id == subject_id,
        ContentStrand.grade_id == grade_id
    ).order_by(ContentStrand.order_index).all()

    strands_tree: List[TreeStrand] = []

    for st in strands:
        topics_tree: List[TreeTopic] = []
        for tp in sorted(st.topics, key=lambda x: x.order_index):
            lessons_tree: List[TreeLesson] = []
            for ls in sorted(tp.lessons, key=lambda x: x.order_index):
                lo_tree: List[TreeLearningOutcome] = []
                for lo in sorted(ls.learning_outcomes, key=lambda x: x.order_index):
                    arch_tree = [
                        TreeArchetype(
                            id=ar.id,
                            code=ar.code,
                            name=ar.name,
                            description=ar.description,
                            order_index=ar.order_index
                        )
                        for ar in sorted(lo.problem_archetypes, key=lambda x: x.order_index)
                    ]
                    lo_tree.append(
                        TreeLearningOutcome(
                            id=lo.id,
                            code=lo.code,
                            description=lo.description,
                            cognitive_level=lo.cognitive_level,
                            order_index=lo.order_index,
                            archetypes=arch_tree
                        )
                    )
                lessons_tree.append(
                    TreeLesson(
                        id=ls.id,
                        code=ls.code,
                        name=ls.name,
                        order_index=ls.order_index,
                        learning_outcomes=lo_tree
                    )
                )
            topics_tree.append(
                TreeTopic(
                    id=tp.id,
                    code=tp.code,
                    name=tp.name,
                    order_index=tp.order_index,
                    lessons=lessons_tree
                )
            )
        strands_tree.append(
            TreeStrand(
                id=st.id,
                code=st.code,
                name=st.name,
                order_index=st.order_index,
                topics=topics_tree
            )
        )

    return TaxonomyTreeResponse(
        subject_id=subj.id,
        subject_name=subj.name,
        grade_id=grd.id,
        grade_name=grd.name,
        strands=strands_tree
    )
