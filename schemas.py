"""
Database Schemas for UniGrasp

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Contact(BaseModel):
    """
    Contact form submissions
    Collection: "contact"
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    message: Optional[str] = Field(None, description="Message from user")
    interest: Optional[str] = Field(None, description="Area of interest, e.g., Career Switch, Resume Review")


class Consultation(BaseModel):
    """
    Consultation scheduling intents
    Collection: "consultation"
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    preferred_time: Optional[str] = Field(None, description="Preferred time slot or timezone info")
    notes: Optional[str] = Field(None, description="Additional notes")
    plan: Optional[str] = Field(None, description="Selected plan e.g., Starter, Pro, Elite")


class BlogPost(BaseModel):
    """
    Blog posts
    Collection: "blogpost"
    """
    title: str = Field(..., description="Blog post title")
    slug: str = Field(..., description="URL slug")
    excerpt: Optional[str] = Field(None, description="Short summary")
    content: str = Field(..., description="Markdown or HTML content")
    author: Optional[str] = Field("UniGrasp Team", description="Author name")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")


class Resource(BaseModel):
    """
    Resources (guides, templates, links)
    Collection: "resource"
    """
    title: str = Field(..., description="Resource title")
    category: Optional[str] = Field(None, description="Category e.g., Resume, Interview, Roadmaps")
    url: Optional[str] = Field(None, description="External link if applicable")
    description: Optional[str] = Field(None, description="Short description")
