// ==============================|| SYS - POST INSERT  ||============================== //

import axios from "axios";
export default async function handler(req, res) {
    // http url
    const api_path = "/sys/insert";
    const url = `${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}${api_path}/`;
    //console.log("-----url2", url);
    // http payload (data)
    const payload = req.body;

    // http config
    const token = req.headers['authorization'];
    //console.log("-----token", token);
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    // console.log("#####-----ip", ip);
    const config = {
        headers: {
            'accept': 'application/json',
            'Authorization': token,
            'X-Forwarded-For': ip,
            'Content-Type': 'application/json',
        }
    };

    // send axios http request
    try {
        const response = await axios.post(
            url,
            payload,
            config,
        )
        return res.status(response.status).json(response.data);
    } catch (error) {
        // console.log('Error\n', error);
        return res.status(error.response.status).json(error);
    }
}