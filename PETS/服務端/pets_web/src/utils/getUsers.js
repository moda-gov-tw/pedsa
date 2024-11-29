import axios from "axios";

async function getALLUsers(setAllUsers, token) {
    await axios.get("/api/user/get_user/",{
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
        .then((response) => {
            // console.log('get all users', response.data.obj);
            setAllUsers(response.data.obj);
        })
        .catch((response) => {
        //   console.log('error', response);
        });
}
export default getALLUsers;