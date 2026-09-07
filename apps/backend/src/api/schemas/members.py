"""Bundestag member response schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MemberImageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    media_url: str
    commons_file_page_url: str
    author: str | None = None
    attribution_text: str | None = None
    license_name: str | None = None
    license_url: str | None = None


class MemberTermSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    electoral_term: int
    active: bool


class MemberOfficeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    office_type: str
    label: str | None = None
    raw_address: str


class MemberContactPointSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contact_type: str
    label: str
    url: str


class MemberMandateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mandate_type: str
    constituency_number: int | None = None
    constituency_name: str | None = None
    constituency_url: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class MemberExternalProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: str
    raw_label: str
    url: str


class MemberAffiliationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    organization_name: str
    organization_url: str | None = None
    role_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class MemberSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mdb_id: int
    first_name: str | None = None
    last_name: str
    name_prefix: str | None = None
    occupation: str | None = None
    parliamentary_group: str | None = None
    electoral_terms: list[int] = Field(default_factory=list)
    image_url: str | None = None


class MemberDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mdb_id: int
    first_name: str | None = None
    last_name: str
    name_prefix: str | None = None
    occupation: str | None = None
    parliamentary_group: str | None = None
    observed_at: datetime | None = None
    source_document_id: UUID | None = None

    image: MemberImageSchema | None = None
    terms: list[MemberTermSchema] = Field(default_factory=list)
    offices: list[MemberOfficeSchema] = Field(default_factory=list)
    contact_points: list[MemberContactPointSchema] = Field(default_factory=list)
    mandates: list[MemberMandateSchema] = Field(default_factory=list)
    external_profiles: list[MemberExternalProfileSchema] = Field(default_factory=list)
    affiliations: list[MemberAffiliationSchema] = Field(default_factory=list)
