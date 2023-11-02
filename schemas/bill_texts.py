from pydantic import BaseModel, Field


class BillTextUsSectionSchema(BaseModel):
    """'bill_text_us' section schema."""

    text: str | None = Field(None)
    id: str | None = Field(None)
    header: str | None = Field(None)


class BillTextUsItemSchema(BaseModel):
    """'bill_text_us' single item schema."""

    id: str = Field()
    congress: int = Field()
    bill_type: str = Field()
    bill_number: int = Field()
    bill_version: str = Field()
    title: str | None = Field(None)
    sections: list[BillTextUsSectionSchema] = Field()
    sections_length: int = Field()
    text: str = Field()
    text_length: int = Field()
