// ==============================|| PROJECT - PUT ML STOP  ||============================== //

import axios from "axios";
export default async function handler(req, res) {
    // http url
    const api_path = "/projects/mlstop";
    const url = `${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}${api_path}?project_id=${req.body['project_id']}`;

    // http config
    // console.log("request",req.headers)
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    const config = {
        headers: {
            'accept': 'application/json',
            'Authorization': token,
            'X-Forwarded-For': ip,
        }
    };

    // send axios http request
    try {
        const response = await axios.put(
            url,
            null,
            config,
        )
        return res.status(response.status).json(response.data);
    } catch (error) {
        // console.log('Error\n', error);
        return res.status(error.response.status).json(error);
    }
}