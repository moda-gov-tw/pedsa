import axios from "axios";

export default async function handler(req, res) {
    const group_id = Object.values(req.query)[0][0];

    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;

	const returnData = await axios
        .delete(`${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}/groups/delete/${group_id}`,
            {headers: {
                'Authorization': token,
                'X-Forwarded-For': ip,
            }})
        .then((response) => {
          res.status(200).json(response.data);
        })
        .catch((error) => {
          // console.log(error.response.data);
          res.status(400).json(error.response.data);
        });
        return returnData;
}