from pydantic import BaseModel

#Data Definition
class RealEstate(BaseModel):
    id: int
    name: str
    address: str
    location: str
    price: int
    area: int
    bedroom: int
    bathroom: int
    description: str
    image: str
    type: str
    status: str

class DemographicData(BaseModel):
    population: int
    populationDensity: int
    location: str