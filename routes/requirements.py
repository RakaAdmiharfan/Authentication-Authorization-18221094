from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import json
from models.requirements import RealEstate, DemographicData
from models.users import UserJSON
from routes.auth import get_current_user


# Load data from the JSON file
with open("data/requirement.json", "r") as json_file:
    data = json.load(json_file)

# Assign the tables
demographicData = data.get("demographicData", [])
realEstate = data.get("realEstate", [])

getter_router = APIRouter(tags=["Getters"])
admin_router = APIRouter(tags=["Admin"])


#-----------------------------Getters-----------------------------------#
# GET real estate data
@getter_router.get("/realEstate", response_model=List[RealEstate])
async def get_real_estate_data() -> List[RealEstate]:
    return realEstate

# GET demographic data
@getter_router.get("/demographic", response_model=List[DemographicData])
async def get_demographic_data() -> List[DemographicData]:
    return demographicData

# GET Real Estate Data by ID
@getter_router.get("/realEstate/{id}", response_model=RealEstate)
async def get_real_estate_data_by_id(id: int) -> RealEstate:
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    real_estate_data = next((req for req in realEstate if req.get("id") == id), None)
    return RealEstate(**real_estate_data)

# GET Demographic Data by Location
@getter_router.get("/demographic/{location}", response_model=DemographicData)
async def get_demographic_data_by_location(location: str) -> DemographicData:
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    demographic_data = next((req for req in demographicData if req.get("location") == location), None)
    return DemographicData(**demographic_data)

#-----------------------------Post-----------------------------------#
#POST Real Estate Data
@admin_router.post("/realEstate", response_model=RealEstate)
async def addRealEstate(change: RealEstate, user: UserJSON = Depends(get_current_user)):
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a new real estate"
        )
    
    try:
        change_dict = change.dict()
    except Exception as e:
        raise HTTPException(status_code=422, detail="Invalid input data")

    realEstate_data = data.get("realEstate")

    # Extracting used IDs
    used_ids = {realEstate.get("id") for realEstate in realEstate_data}

    # Finding the smallest available ID
    available_id = 1
    while available_id in used_ids:
        available_id += 1

    # Setting the new real estate ID
    change.id = available_id

    # Adding the new data to the list
    realEstate_data.append(change.dict())

    # Saving data back to the JSON file
    with open('data/requirement.json', "w") as write_file:
        json.dump(data, write_file, indent=4)

    return change  # Returning the Pydantic model directly

#POST Demographic Data
@admin_router.post("/demographic", response_model=DemographicData)
async def addDemographic(change: DemographicData, user: UserJSON = Depends(get_current_user)):
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a new demographic data"
        )

    # Validasi apakah data sesuai dengan model demographicData
    try:
        change_dict = change.dict()
    except Exception as e:
        raise HTTPException(status_code=422, detail="Invalid input data")

    demographicData_data = data.get("demographicData", [])

    # Check if the location already exists
    existing_location = next(
        (item for item in demographicData_data if item["location"] == change.location),
        None
    )

    if existing_location:
        raise HTTPException(status_code=400, detail="Location already exists")

    # Append the new demographic data to the list
    demographicData_data.append(change.dict())

    # Update the data dictionary with the new demographic data
    data["demographicData"] = demographicData_data

    with open('data/requirement.json', "w") as write_file:
        json.dump(data, write_file, indent=4)

    # Return the newly added demographic data
    return change

#-----------------------------Put-----------------------------------#
# PUT Real Estate Data
@admin_router.put("/realEstate/{id}", response_model=RealEstate)
async def updateRealEstate(id: int, newData: RealEstate, user: UserJSON = Depends(get_current_user)):
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this requirement"
        )
    
    realEstate_data = data.get("realEstate")
    for i, new in enumerate(realEstate_data):
        if new.get("id") == id:
            newData.id = id
            realEstate_data[i] = newData.dict()
            with open('data/requirement.json', "w") as write_file:
                json.dump(data, write_file, indent=4)
            return newData
    raise HTTPException(status_code=404, detail="realEstate not found")

# PUT Demographic Data
@admin_router.put("/demographic/{location}", response_model=DemographicData)
async def updateDemographic(location: str, newData: DemographicData, user: UserJSON = Depends(get_current_user)):
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this requirement"
        )
    
    demographicData_data = data.get("demographicData")
    for i, new in enumerate(demographicData_data):
        if new.get("location") == location:
            newData.location = location
            demographicData_data[i] = newData.dict()
            with open('data/requirement.json', "w") as write_file:
                json.dump(data, write_file, indent=4)
            return newData
    raise HTTPException(status_code=404, detail="demographicData not found")

#------------------------------Delete----------------------------------#
# DELETE Real Estate Data
@admin_router.delete("/realEstate/{id}")
async def deleteRealEstate(id: int, user: UserJSON = Depends(get_current_user)):
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this requirement"
        )
    
    realEstate_data = data.get("realEstate")
    for i, new in enumerate(realEstate_data):
        if new.get("id") == id:
            realEstate_data.pop(i)
            with open('data/requirement.json', "w") as write_file:
                json.dump(data, write_file, indent=4)
            return {
                "message": "Real Estate deleted successfully"
            }
    raise HTTPException(status_code=404, detail="realEstate not found")

# DELETE Demographic Data
@admin_router.delete("/demographic/{location}")
async def deleteDemographic(location: str, user: UserJSON = Depends(get_current_user)):
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this requirement"
        )
    
    demographicData_data = data.get("demographicData")
    
    for i, new in enumerate(demographicData_data):
        if new.get("location") == location:
            demographicData_data.pop(i)
            with open('data/requirement.json', "w") as write_file:
                json.dump(data, write_file, indent=4)
            return {
                "message": "Demographic Data deleted successfully"
            }
    raise HTTPException(status_code=404, detail="demographicData not found")