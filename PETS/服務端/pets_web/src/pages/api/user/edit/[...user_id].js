// ==============================|| USER - EDIT USER  ||============================== //
import axios from "axios";
export default async function handler(req, res) {
    const user_id = Object.values(req.query)[0][0];
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    try {
        const returnData = await axios.put(`${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}/users/update/${user_id}`,
            req.body,
            {
                headers: {
                    'Authorization': token,
                    'X-Forwarded-For': ip,
                }
            }
        )
            // .then(response => response.json())
            .then((response) => {
                if (response.status) {
                    // console.log('edit users', response);
                    res.status(200).json(response.data);
                } else {
                    // console.log('edit users fail', response);
                    res.status(400).json({ message: '編輯人員失敗' });
                }
            })
            .catch((err) => {
                // console.log('400 err', err);
                res.status(400).json((err));
            });
        return returnData;
    } catch (err) {
        // console.log('500 err', err);
        return res.status(500).json(err);
    }
}