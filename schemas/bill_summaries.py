from pydantic import BaseModel, Field


class BillSummaryUsSectionSchema(BaseModel):
    """'bill_summary_us' section schema."""

    text: str | None = Field(None)
    id: str | None = Field(None)
    header: str | None = Field(None)


class BillSummaryUsItemSchema(BaseModel):
    """'bill_summary_us' single item schema."""

    id: str = Field()
    congress: int = Field()
    bill_type: str = Field()
    bill_number: int = Field()
    bill_version: str = Field()
    sections: list[BillSummaryUsSectionSchema] = Field()
    sections_length: int = Field()
    text: str = Field()
    text_length: int = Field()
    summary: str = Field()
    summary_length: int = Field()
    title: str = Field()
