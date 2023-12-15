import axios from "axios";

async function getALLGroups(setAllGroups, token) {
    await axios.get("/api/group/get_group/",{
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
        .then((response) => {
            // console.log('get all groups', response.data.obj);
            setAllGroups(response.data.obj);
        })
        .catch((response) => {
          console.log('error', response);
        });
}

export default getALLGroups;