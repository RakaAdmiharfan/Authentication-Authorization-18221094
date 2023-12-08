from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import json
from models.requirements import RealEstate, DemographicData, DataListrik
from models.users import UserJSON
from routes.auth import get_current_user
import httpx


# Load data from the JSON file
with open("data/requirement.json", "r") as json_file:
    data = json.load(json_file)

# Assign the tables
demographicData = data.get("demographicData", [])
realEstate = data.get("realEstate", [])

getter_router = APIRouter(tags=["Getters Layanan Lama"])
admin_router = APIRouter(tags=["CRUD Layanan Lama"])
friend_router = APIRouter(tags=["Layanan Baru (Utama)"])
support_router = APIRouter(tags=["Layanan Baru (Tambahan)"])

#-----------------------------API Orang-----------------------------------#
#GET Data Listrik - Real Estate
@friend_router.get("/getListrikRealEstate", response_model=List[dict])
async def get_listrik_real_estate_data(user: UserJSON = Depends(get_current_user)) -> List[dict]:
    try:
        # Get real estate data
        real_estate_data = realEstate

        # Lakukan permintaan HTTP ke API eksternal untuk mendapatkan data listrik
        async with httpx.AsyncClient() as client:
            response = await client.get("https://integration-api-amjad.victoriousplant-40d1c733.australiaeast.azurecontainerapps.io/umum/data_listrik")
        
        # Periksa apakah permintaan berhasil (kode status 200)
        response.raise_for_status()

        # Ubah respons JSON menjadi bentuk yang sesuai dengan model Anda
        listrik_data = response.json()

        # Tambahkan realEstateID ke setiap data listrik based on id in realEstateData
        for idx, data in enumerate(listrik_data):
            # Check if the index is within the range of realEstateData
            if idx < len(real_estate_data):
                # Assign the realEstateID based on the id in realEstateData
                data["realEstateID"] = real_estate_data[idx].get("id")
            else:
                # Handle the case where there are more entries in listrik_data than real_estate_data
                # You may want to assign a default value or handle this case based on your requirements
                data["realEstateID"] = None  # Set to a default value or handle as needed

        # Join the real estate data with listrik data based on realEstateID and id
        joined_data = []
        for real_estate_entry in real_estate_data:
            for listrik_entry in listrik_data:
                if listrik_entry.get("realEstateID") == real_estate_entry.get("id"):
                    # Combine the entries into a single dictionary with selected fields for listrikData
                    joined_entry = {
                        "realEstateID": real_estate_entry["id"],
                        "realEstateData": real_estate_entry,
                        "listrikData": {
                            "tanggal": listrik_entry["tanggal"],
                            "jam": listrik_entry["jam"],
                            "jumlahListrik": listrik_entry["jumlahListrik"],
                        }
                    }
                    joined_data.append(joined_entry)

        return joined_data

    except httpx.HTTPError as e:
        # Tangani kesalahan HTTP jika terjadi
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except Exception as e:
        # Tangani kesalahan umum jika terjadi
        raise HTTPException(status_code=500, detail=str(e))
    
# POST DATA
@friend_router.post("/post/dataListrik-realEstate", response_model=DataListrik)
async def addDataListrikRealEstate(change: DataListrik, user: UserJSON = Depends(get_current_user)):
    try:
        change_dict = change.dict()
    except Exception as e:
        raise HTTPException(status_code=422, detail="Invalid input data")

    url = "https://integration-api-amjad.victoriousplant-40d1c733.australiaeast.azurecontainerapps.io/administrator/data_listik"
    headers = {"Authorization": f"Bearer {user.token_teman}"}

    try:
        # Get Data Real Estate
        real_estate_data = await get_real_estate_data(user)

        # Get Data Listrik
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://integration-api-amjad.victoriousplant-40d1c733.australiaeast.azurecontainerapps.io/umum/data_listrik"
            )

        response.raise_for_status()
        listrik_data = response.json()

        # Check if the length of dataListrik is not longer than dataRealEstate
        if len(listrik_data) >= len(real_estate_data):
            raise HTTPException(status_code=400, detail="Cannot add more dataListrik entries")

        # Make the post request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=change_dict, headers=headers)

        response.raise_for_status()
        updateDataListrik = response.json()

        return updateDataListrik

    except httpx.HTTPError as e:
        # Handle HTTP errors
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail="Cannot add more dataListrik entries")

#PUT DATA
@friend_router.put("/put/dataListrik-realEstate", response_model= DataListrik)
async def updateDataListrikRealEstate(change: DataListrik, user: UserJSON = Depends(get_current_user)):

    try:
        change_dict = change.dict()
    except Exception as e:
        raise HTTPException(status_code=422, detail="Invalid input data")

    # print(user.token_teman)
    url = "https://integration-api-amjad.victoriousplant-40d1c733.australiaeast.azurecontainerapps.io/administrator/edit_listrik"

    headers = {
        "Authorization": f"Bearer {user.token_teman}"
    }

    try:
        # Make the PUT request
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=change_dict, headers=headers)
        
        # Check if the request was successful (status code 2xx)
        response.raise_for_status()

        # Parse the JSON response
        updateDataListrik = response.json()
        
        return updateDataListrik

    except httpx.HTTPError as e:
        # Handle HTTP errors
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="API Update Data Listrik not found or error")
        else:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=str(e))
    
# # DELETE DATA
@friend_router.delete("/delete/dataListrik-realEstate/{username}")
async def deleteDataListrikRealEstate(username: str, user: UserJSON = Depends(get_current_user)):
    try:
        # Get the authentication token from the user
        auth_token = user.token_teman

        # Make the DELETE request with the proper authorization header
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"https://integration-api-amjad.victoriousplant-40d1c733.australiaeast.azurecontainerapps.io/administratordelete_listrik/{username}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Check if the request was successful (status code 2xx)
        response.raise_for_status()

        # Parse the JSON response
        deleteDataListrik = response.json()

        return deleteDataListrik

    except httpx.HTTPError as e:
        # Handle HTTP errors
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=str(e))


#-----------------------------Getters-----------------------------------#
# GET real estate data
@support_router.get("/realEstate", response_model=List[RealEstate])
async def get_real_estate_data(user: UserJSON = Depends(get_current_user)) -> List[RealEstate]:
    return realEstate

# GET demographic data
@getter_router.get("/demographic", response_model=List[DemographicData])
async def get_demographic_data(user: UserJSON = Depends(get_current_user)) -> List[DemographicData]:
    return demographicData

# GET Real Estate Data by ID
@support_router.get("/realEstate/{id}", response_model=RealEstate)
async def get_real_estate_data_by_id(id: int, user: UserJSON = Depends(get_current_user)) -> RealEstate:
    real_estate_data = next((req for req in realEstate if req.get("id") == id), None)
    return RealEstate(**real_estate_data)

# GET Demographic Data by Location
@getter_router.get("/demographic/{location}", response_model=DemographicData)
async def get_demographic_data_by_location(location: str, user: UserJSON = Depends(get_current_user)) -> DemographicData:
    demographic_data = next((req for req in demographicData if req.get("location") == location), None)
    return DemographicData(**demographic_data)

#-----------------------------Post-----------------------------------#
#POST Real Estate Data
@support_router.post("/realEstate", response_model=RealEstate)
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
@support_router.put("/realEstate/{id}", response_model=RealEstate)
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
@support_router.delete("/realEstate/{id}")
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