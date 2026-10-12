from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SampleInfo(BaseModel):
    filename: str
    is_defective: bool
    class_id: int
    class_name: str
    severity: str
    quality_grade: str
    defect_area_pct: float
    description: str
    encoded_pixels: Optional[str] = ''

class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class DefectRegion(BaseModel):
    region_id: int
    bbox: BoundingBox
    area_pixels: int
    perimeter: float
    polygon: List[List[int]]

class InspectionResult(BaseModel):
    inspection_id: str
    timestamp: str
    source_filename: str
    is_defective: bool
    defect_probability: float
    quality_score: float
    quality_grade: str
    severity: str
    verdict: str
    verdict_badge: str
    class_id: int
    class_name: str
    class_color: str
    class_metadata: Dict[str, Any]
    defect_area_pct: float
    total_defect_pixels: int
    regions_count: int
    max_defect_region_area: int
    regions: List[Dict[str, Any]]
    predicted_rle: str
    image_dimensions: Dict[str, int]
    class_probabilities: Dict[str, float]
    visualizations: Dict[str, str]

class BatchSummary(BaseModel):
    batch_id: str
    total_inspected: int
    defective_count: int
    defect_free_count: int
    average_quality_score: float
    defect_rate_pct: float
    timestamp: str
    results: List[Dict[str, Any]]

class AnalyticsData(BaseModel):
    total_inspections: int
    pass_rate: float
    defect_distribution: Dict[str, int]
    model_metrics: Dict[str, Any]
    hardware_info: Dict[str, Any]
