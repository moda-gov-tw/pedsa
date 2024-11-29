// ==============================|| PROJECT - CHECK PROJECT NAME  ||============================== //

import axios from "axios";
export default async function handler(req, res) {
    // http url
    const api_path = "/projects/checkprojcht";
    const url = `${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}${api_path}`;
    // http config
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    const config = {
        params: req.body,
        headers: {
            'accept': 'application/json',
            'Authorization': token,
            'X-Forwarded-For': ip,
        }
    };

    // send axios http request
    try {
        const response = await axios.post(url, null, config);
        // console.log('response', response);
        return res.status(response.status).json(response.data);
    } catch (error) {
        // console.log('Error\n', error);
        return res.status(error.response.status).json(error);
    }
}