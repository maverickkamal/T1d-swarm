from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class EventDetails(BaseModel):
    estimated_carbs_g: Optional[int] = Field(None, description="Estimated carbohydrates consumed in grams.")
    meal_type: Optional[str] = Field(None, description="Type of meal (e.g., 'snack', 'lunch', 'dinner').")
    exercise_type: Optional[str] = Field(None, description="Type of exercise (e.g., 'running', 'walking', 'swimming').")
    exercise_duration_min: Optional[int] = Field(None, description="Duration of exercise in minutes.")
    intensity: Optional[str] = Field(None, description="Intensity of activity (e.g., 'low', 'moderate', 'high').")
    symptoms: Optional[List[str]] = Field(None, description="List of symptoms experienced (e.g., ['shaky', 'sweaty']).")
    notes: Optional[str] = Field(None, description="Any additional relevant notes about the event.")
    # Add any other potential keys from your examples here!
    # For example, if you expect 'stress_level':
    # stress_level: Optional[str] = Field(None, description="Level of stress (e.g., 'low', 'medium', 'high').")
    # If 'data_quality_issues' can be a specific type or just True/False
    data_quality_issues: Optional[bool] = Field(None, description="Indicates if there are issues with the CGM data quality.")




class ModelInput(BaseModel):
    glucose_value: int = Field(0, alias='glucose_value', description='The glucose reading of a patient by the CGM')
    trend_arrow: str = Field("...", alias='trend_arrow',
                             description="An arrow showing how quickly the patients glucose is rising,"
                                         "return 'DoubleUp' to indicate patients glucose is rising rapidly,"
                                         "return 'SingleUp' to indicate patients glucose is rising,"
                                         "return 'FortyFiveUp' to indicate patients glucose is rising slowly,"
                                         "return 'Flat' to indicate patients glucose is constant,"
                                         "return 'FortyFiveDown' to indicate patients glucose is falling slowly,"
                                         "return 'SingleDown' to indicate patients glucose is falling,"
                                         "return 'DoubleDown' to indicate patients glucose is falling rapidly,"
                                         "return 'NOT_COMPUTABLE' to indicate the CGM has no reading of patients glucose,"
                                         "return 'Error' to indicate issues with CGM reading")
    unit: str = Field("mg/dL", alias='unit', description='The unit of the glucose reading')
    data_quality_issues: str = Field("None", alias='problems',
                                     description="Indicates whether the cgm is experiencing issues regarding reading data")
    timestamp: str = Field(..., alias='timestamp',
                                description='The date and time the glucose reading was taken')


class ModelOutput(BaseModel):
    event_type : str = Field("...", alias='event_type', description='The event type of what the person might be doing that correlates with the glucose reading')
    description: str = Field("...", alias='description_raw', description='The raw description of the event')
    details: EventDetails = Field(..., alias='parsed_details', description='A JSON object detailing the most important parts of an event, this is used to generate insights as to how to treat the patients glucose levels',)
    timestamp: datetime = Field(datetime.utcnow(), alias='timestamp_event', description='The time the event occurred')
