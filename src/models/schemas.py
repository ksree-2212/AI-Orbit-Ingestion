"""
Data schema definitions for the AI Orbit Data Ingestion Pipeline.
Implements Common Entity Schema (Section 4.1) and Specialized Metadata schemas (Section 4.2).
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

AI_ORBIT_NAMESPACE = uuid.UUID("a1000000-0000-0000-0000-000000000001")


class EntityType(str, Enum):
    TOOL = "Tool"
    TASK = "Task"
    COMPANY = "Company"
    NEWS = "News"
    VIDEO = "Video"
    ROBOT = "Robot"
    DEVICE = "Device"
    MODEL = "Model"
    REPOSITORY = "Repository"
    MCP = "MCP"
    COLLECTION = "Collection"
    PERSONAL = "Personal"
    CREATIVE = "Creative"
    RECENTLY_ADDED = "RecentlyAdded"


class RelationshipType(str, Enum):
    DEVELOPED_BY = "DEVELOPED_BY"          # Tool/Model/Robot/Device/MCP -> Company
    DEVELOPS = "DEVELOPS"                  # Company -> Tool/Model/Robot/Device/MCP
    SOLVES_TASK = "SOLVES_TASK"            # Tool -> Task
    INTEGRATES_WITH = "INTEGRATES_WITH"    # MCP -> Tool
    RUNS_ON = "RUNS_ON"                    # Model -> Device
    RUNS = "RUNS"                          # Device -> Model
    POWERS = "POWERS"                      # Model -> Tool / Personal / Creative
    POWERED_BY = "POWERED_BY"              # Tool / Personal / Creative -> Model
    IMPLEMENTS = "IMPLEMENTS"              # Repository -> Tool / Model / MCP
    IMPLEMENTED_BY = "IMPLEMENTED_BY"      # Tool / Model / MCP -> Repository
    COVERS = "COVERS"                      # News -> Company / Model / Tool / Robot
    COVERED_BY = "COVERED_BY"              # Company / Model / Tool / Robot -> News
    REVIEWS = "REVIEWS"                    # Video -> Model / Tool / Robot / Device
    REVIEWED_BY = "REVIEWED_BY"            # Model / Tool / Robot / Device -> Video
    CONTAINS = "CONTAINS"                  # Collection -> Tool / Model / Repository / MCP
    CONTAINED_IN = "CONTAINED_IN"          # Entity -> Collection


class SourceInfo(BaseModel):
    name: str = Field(..., description="Source provider name (e.g. GitHub, Hugging Face, TechCrunch)")
    url: str = Field(..., description="Source origin URL")


class BaseEntity(BaseModel):
    """
    Common Entity Schema compliant with Section 4.1 of AI Orbit Spec:
    {
      "id": "stable-generated-uuid",
      "entity_type": "string",
      "name": "string",
      "description": "string",
      "url": "string",
      "categories": ["string"],
      "source": { "name": "string", "url": "string" }
    }
    """
    id: str = Field(..., description="Stable deterministic UUID (uuid5)")
    entity_type: EntityType = Field(..., description="Entity classification category")
    name: str = Field(..., description="Canonical entity name")
    description: str = Field(..., description="Sanitized and informative description")
    url: str = Field(..., description="Canonical normalized URL")
    categories: List[str] = Field(default_factory=list, description="Categorization taxonomy tags")
    source: SourceInfo = Field(..., description="Ingestion source attribution")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific metadata")
    created_at: Optional[str] = Field(None, description="ISO timestamp of record creation/publication")
    updated_at: Optional[str] = Field(None, description="ISO timestamp of last update")


class ModelEntity(BaseEntity):
    license: Optional[str] = Field(None, description="Model open source or proprietary license")
    modalities: List[str] = Field(default_factory=list, description="Supported input/output modalities")
    provider: Optional[str] = Field(None, description="Organization or lab providing the model")
    context_window: Optional[int] = Field(None, description="Maximum context window in tokens")
    parameter_count: Optional[str] = Field(None, description="Model size (e.g. 70B, 405B, MoE 8x22B)")
    architecture: Optional[str] = Field(None, description="Underlying architecture")


class RepositoryEntity(BaseEntity):
    stars: Optional[int] = Field(0, description="GitHub stargazers count")
    forks: Optional[int] = Field(0, description="GitHub forks count")
    primary_language: Optional[str] = Field(None, description="Primary programming language")
    last_updated: Optional[str] = Field(None, description="Last commit or update timestamp")
    open_issues: Optional[int] = Field(0, description="Number of open issues")
    topics: List[str] = Field(default_factory=list, description="Repository topic tags")


class MCPEntity(BaseEntity):
    installation_methods: List[str] = Field(default_factory=list, description="Install commands e.g. npm, uvx, docker")
    runtime_requirements: Optional[str] = Field(None, description="Runtime requirements e.g. Node.js >= 18, Python 3.10")
    transport: Optional[str] = Field("stdio", description="MCP communication transport: stdio, sse, http")
    vendor: Optional[str] = Field(None, description="Vendor or developer organization")
    compatible_clients: List[str] = Field(default_factory=list, description="Supported MCP clients (e.g. Claude Desktop, Cursor)")


class CompanyEntity(BaseEntity):
    founding_year: Optional[int] = Field(None, description="Year established")
    industry_sector: Optional[str] = Field(None, description="AI sector focus")
    headquarters: Optional[str] = Field(None, description="Location of headquarters")
    total_funding: Optional[str] = Field(None, description="Reported total capital raised")
    valuation: Optional[str] = Field(None, description="Estimated enterprise valuation")
    key_people: List[str] = Field(default_factory=list, description="Founders or executive leaders")


class ToolEntity(BaseEntity):
    pricing_model: Optional[str] = Field(None, description="Pricing tier: Free, Freemium, Commercial, Open Source")
    platform: List[str] = Field(default_factory=list, description="Web, Desktop, CLI, API, Mobile")
    primary_use_case: Optional[str] = Field(None, description="Core workflow addressed")


class TaskEntity(BaseEntity):
    difficulty_level: Optional[str] = Field("Intermediate", description="Beginner, Intermediate, Advanced")
    domain: Optional[str] = Field(None, description="Functional AI domain (e.g. Coding, Vision, Synthesis)")
    typical_workflows: List[str] = Field(default_factory=list, description="Step-by-step user workflows")


class RobotEntity(BaseEntity):
    manufacturer: Optional[str] = Field(None, description="Robotics manufacturing company")
    locomotion_type: Optional[str] = Field(None, description="Bipedal, Quadrupedal, Wheeled, Stationary Arm")
    payload_capacity_kg: Optional[float] = Field(None, description="Payload capacity in kilograms")
    degrees_of_freedom: Optional[int] = Field(None, description="Actuator DoF count")
    runtime_hours: Optional[float] = Field(None, description="Battery battery life in hours")
    application_domain: Optional[str] = Field(None, description="Logistics, Manufacturing, Healthcare, Research")


class DeviceEntity(BaseEntity):
    manufacturer: Optional[str] = Field(None, description="Hardware manufacturer")
    chip_processor: Optional[str] = Field(None, description="AI acceleration processor or SoC")
    form_factor: Optional[str] = Field(None, description="Server GPU, Wearable, Edge Board, Mobile")
    memory_ram: Optional[str] = Field(None, description="Memory capacity and bandwidth")
    compute_capacity_tops: Optional[str] = Field(None, description="AI compute power (TOPS or TFLOPS)")
    power_draw_w: Optional[int] = Field(None, description="Thermal Design Power / Power draw in watts")


class NewsEntity(BaseEntity):
    published_at: Optional[str] = Field(None, description="ISO publication date")
    author: Optional[str] = Field(None, description="Author or journalist")
    sentiment: Optional[str] = Field("Neutral", description="Positive, Neutral, Analytical, Critical")
    summary: Optional[str] = Field(None, description="Executive news summary")
    primary_topic: Optional[str] = Field(None, description="Core topic focus")


class VideoEntity(BaseEntity):
    channel: Optional[str] = Field(None, description="YouTube channel or creator name")
    duration_seconds: Optional[int] = Field(None, description="Video runtime in seconds")
    view_count: Optional[int] = Field(0, description="Approximate view count")
    published_at: Optional[str] = Field(None, description="Publication timestamp")
    video_format: Optional[str] = Field("Tutorial", description="Tutorial, Deep Dive, Benchmark, Demo, Interview")


class CollectionEntity(BaseEntity):
    curator: Optional[str] = Field(None, description="Curator name or organization")
    total_items: Optional[int] = Field(0, description="Number of items included")
    item_references: List[str] = Field(default_factory=list, description="IDs or names of curated items")


class PersonalEntity(BaseEntity):
    privacy_level: Optional[str] = Field("Local First", description="Local First, Cloud Encrypted, Hybrid")
    input_modalities: List[str] = Field(default_factory=list, description="Voice, Screen, Camera, Text")
    os_support: List[str] = Field(default_factory=list, description="macOS, Windows, iOS, Android, Linux")


class CreativeEntity(BaseEntity):
    artistic_domain: Optional[str] = Field(None, description="Image, Video, Music, 3D, Voice Synthesis")
    output_formats: List[str] = Field(default_factory=list, description="PNG, SVG, MP4, FLAC, OBJ, etc.")
    generation_speed: Optional[str] = Field(None, description="Real-time, Sub-second, Batch")


class Relationship(BaseModel):
    """
    Graph edge mapping the interconnectedness of the AI ecosystem.
    Complies with Section 5 of AI Orbit Spec.
    """
    id: str = Field(..., description="Deterministic relationship UUID")
    source_id: str = Field(..., description="UUID of source entity")
    source_name: str = Field(..., description="Name of source entity")
    source_type: EntityType = Field(..., description="Type of source entity")
    relationship_type: RelationshipType = Field(..., description="Typed relationship predicate")
    target_id: str = Field(..., description="UUID of target entity")
    target_name: str = Field(..., description="Name of target entity")
    target_type: EntityType = Field(..., description="Type of target entity")
    description: str = Field(..., description="Human-readable explanation of relationship")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual relationship attributes")


class PipelineStats(BaseModel):
    total_raw_records: int = 0
    total_entities_processed: int = 0
    total_unique_entities: int = 0
    deduplicated_count: int = 0
    entities_by_category: Dict[str, int] = Field(default_factory=dict)
    total_relationships: int = 0
    relationships_by_type: Dict[str, int] = Field(default_factory=dict)
    validation_status: str = "PASS"
    validation_errors_count: int = 0
    validation_warnings_count: int = 0
    relationship_density: float = 0.0
    quality_score: float = 100.0
