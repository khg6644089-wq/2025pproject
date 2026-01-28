from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from statistics import mean

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="학생 점수 관리 API",
    description="학생들의 점수를 관리하는 FastAPI 샘플 애플리케이션",
    version="1.0.0"
)

# 초기 점수 데이터
score = [
    ['정약용', 85, 90, 80, 75],
    ['이순신', 78, 82, 90, 88],
    ['이율곡', 92, 85, 87, 95],
    ['홍길동', 80, 76, 70, 82],
    ['신사임당', 95, 98, 94, 99],
    ['최무선', 73, 70, 78, 80],
    ['장영실', 88, 89, 85, 92],
    ['김유신', 77, 75, 73, 70],
    ['안중근', 84, 83, 80, 79],
    ['세종대왕', 99, 97, 98, 96]
]
# 각 항목: [이름, 국어, 영어, 수학, 과학]


class ScoreBase(BaseModel):
    name: str = Field(..., min_length=1, description="학생 이름(고유 키로 사용)")
    korean: int = Field(..., ge=0, le=100, description="국어 점수")
    english: int = Field(..., ge=0, le=100, description="영어 점수")
    math: int = Field(..., ge=0, le=100, description="수학 점수")
    science: int = Field(..., ge=0, le=100, description="과학 점수")


class ScoreCreate(ScoreBase):
    pass


class ScoreUpdate(BaseModel):
    korean: Optional[int] = Field(None, ge=0, le=100)
    english: Optional[int] = Field(None, ge=0, le=100)
    math: Optional[int] = Field(None, ge=0, le=100)
    science: Optional[int] = Field(None, ge=0, le=100)


class ScoreOut(ScoreBase):
    total: int
    average: float


def _row_to_out(row: list) -> ScoreOut:
    name, korean, english, math, science = row
    total = int(korean + english + math + science)
    average = float(mean([korean, english, math, science]))
    return ScoreOut(
        name=name,
        korean=korean,
        english=english,
        math=math,
        science=science,
        total=total,
        average=average,
    )


def _find_index_by_name(name: str) -> int:
    for i, row in enumerate(score):
        if row[0] == name:
            return i
    return -1


@app.get("/", tags=["health"])
def health():
    return {"ok": True, "message": "학생 점수 관리 API"}


@app.get("/scores", response_model=List[ScoreOut], tags=["scores"])
def list_scores():
    return [_row_to_out(row) for row in score]


@app.get("/scores/{name}", response_model=ScoreOut, tags=["scores"])
def get_score(name: str):
    idx = _find_index_by_name(name)
    if idx == -1:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다.")
    return _row_to_out(score[idx])


@app.post("/scores", response_model=ScoreOut, status_code=201, tags=["scores"])
def create_score(payload: ScoreCreate):
    if _find_index_by_name(payload.name) != -1:
        raise HTTPException(status_code=409, detail="이미 존재하는 학생입니다.")
    score.append([payload.name, payload.korean, payload.english, payload.math, payload.science])
    return _row_to_out(score[-1])


@app.put("/scores/{name}", response_model=ScoreOut, tags=["scores"])
def replace_score(name: str, payload: ScoreBase):
    idx = _find_index_by_name(name)
    if idx == -1:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다.")

    # 이름 변경 허용(단, 충돌 방지)
    if payload.name != name and _find_index_by_name(payload.name) != -1:
        raise HTTPException(status_code=409, detail="변경하려는 이름이 이미 존재합니다!")

    score[idx] = [payload.name, payload.korean, payload.english, payload.math, payload.science]
    return _row_to_out(score[idx])


@app.patch("/scores/{name}", response_model=ScoreOut, tags=["scores"])
def update_score(name: str, payload: ScoreUpdate):
    idx = _find_index_by_name(name)
    if idx == -1:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다.")

    row = score[idx]
    # row: [name, korean, english, math, science]
    if payload.korean is not None:
        row[1] = payload.korean
    if payload.english is not None:
        row[2] = payload.english
    if payload.math is not None:
        row[3] = payload.math
    if payload.science is not None:
        row[4] = payload.science

    return _row_to_out(row)


@app.delete("/scores/{name}", tags=["scores"])
def delete_score(name: str):
    idx = _find_index_by_name(name)
    if idx == -1:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다.")
    deleted = score.pop(idx)
    return {"deleted": _row_to_out(deleted)}

