// ==============================|| USER - SET　ADMIN ROLE  ||============================== //
import axios from "axios";
export default async function handler(req, res) {
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    console.log('req.body', req.body);
    try {
        const returnData = await axios.post(`${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}/roles/set_admin`,
            req.body,
            {headers: {
                'Authorization': token,
                'X-Forwarded-For': ip,
            }}
        )
            // .then(response => response.json())
            .then((response) => {
                if(response.status) {
                    res.status(200).json(response.data);
                } else{
                    console.log('指派角色', response);
                    res.status(400).json({ message: '指派角色失敗' });
                }
            })
            .catch((err) => {
                console.log('400 err', err);
                res.status(400).json((err));
            });
        return returnData;
    } catch (err) {
        console.log('500 err', err);
        return res.status(500).json(err);
    }
}