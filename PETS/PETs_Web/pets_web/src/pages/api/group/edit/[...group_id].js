// ==============================|| GROUP - CREATE GROUP  ||============================== //
import axios from "axios";
export default async function handler(req, res) {
    const group_id = Object.values(req.query)[0][0];
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    try {
        const returnData = await axios.put(`${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}/groups/update/${group_id}`,
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
                    console.log('edit groups fail', response);
                    res.status(400).json({ message: '編輯單位失敗' });
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