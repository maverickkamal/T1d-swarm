from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ModelOutput(BaseModel):
    glucose_value: int = Field(0, alias='glucose_value', description='The glucose reading of a patient by the CGM')
    trend_arrow: str = Field("...", alias='trend_arrow', description="An arrow showing how quickly the patients glucose is rising,"
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
    data_quality_issues: str = Field("None", alias='problems', description="Indicates whether the cgm is experiencing issues regarding reading data")
    timestamp: datetime = Field(datetime.utcnow(), alias='timestamp', description='The date and time the glucose reading was taken')

