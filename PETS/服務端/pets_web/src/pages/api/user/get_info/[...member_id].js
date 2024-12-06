// ==============================|| USER - EDIT USER  ||============================== //
import axios from "axios";
export default async function handler(req, res) {
    const member_id = Object.values(req.query)[0][0];
    if (!Number.isInteger(Number(member_id))) {
        return res.status(400).json({ message: 'Invalid member_id, it must be an integer' });
    }

    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    try {
        const returnData = await axios.get(`${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}/users/${member_id}`,
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
                    // console.log('edit users fail', response);
                    res.status(400).json({ message: '取得人員資料失敗' });
                }
            })
            .catch((err) => {
                // console.log('get info 400 err', err);
                res.status(400).json((err));
            });
        return returnData;
    } catch (err) {
        // console.log('get info 500 err', err);
        return res.status(500).json(err);
    }
}