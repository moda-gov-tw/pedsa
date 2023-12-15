// ==============================|| PROJECT - GET GAN CHECK STATUS  ||============================== //

import axios from "axios";
export default async function handler(req, res) {
    // http url
    const api_path = "/api/WebAPI/syn_checkstatus";
    const url = `${process.env.SUBSERVICE_SYN_HOST}:${process.env.SUBSERVICE_SYN_PORT}${api_path}`;
    // http config
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    const query = req.query;
    const config = {
        headers: {
            'accept': 'application/json',
            'Authorization': token,
            'X-Forwarded-For': ip,
        },
        params: query,
    };


    // send axios http request
    try {
        const response = await axios.get(url, config);
        return res.status(response.status).json(response.data);
    } catch (error) {
        console.log('Error\n', error);
        return res.status(error.response.status).json(error);
    }
}