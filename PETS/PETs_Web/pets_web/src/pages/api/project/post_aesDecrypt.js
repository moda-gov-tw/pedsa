// ==============================|| PROJECT - POST COMPAREDATA  ||============================== //

import axios from "axios";
export default async function handler(req, res) {
    // http url
    const api_path = "/projects/aesdecrypt";
    const url = `${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}${api_path}?project_id=${req.body["project_id"]}&aes_col=${req.body["aes_col"]}`;
    // http payload (data)
    // const payload = req.body;
    // http config
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    const config = {
        headers: {
            'accept': 'application/json',
            'Authorization': token,
            'X-Forwarded-For': ip,
            // 'Content-Type': 'application/x-www-form-urlencoded',
        }
    };

    // send axios http request
    try {
        const response = await axios.post(
            url,
            // payload,
            config,
        )
        return res.status(response.status).json(response.data);
    } catch (error) {
        console.log('Error\n', error);
        return res.status(error.response.status).json(error);
    }
}