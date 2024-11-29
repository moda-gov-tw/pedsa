// ==============================|| PROJECT - GET SAMPLE DATA ||============================== //
import axios from "axios";
export default async function handler(req, res) {
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    try {
        const returnData = await axios.post(`${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}/projects/sample/`,
            null,
            {
                params: req.body,
                headers: {
                'accept': 'application/json',
                'Authorization': token,
                'X-Forwarded-For': ip,
                'Content-Type': 'application/x-www-form-urlencoded',
            }}
        )
            .then((response) => {
                if(response.status) {
                    res.status(200).json(response.data);
                } else{
                    // console.log('get sample data fail', response);
                    res.status(400).json({ message: 'sample資料取得失敗' });
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