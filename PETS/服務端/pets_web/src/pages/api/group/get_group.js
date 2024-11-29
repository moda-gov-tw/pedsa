// ==============================|| GROUP - GET ALL GROUPS  ||============================== //

export default async function handler(req, res) {
    const token = req.headers['authorization'];
    const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
    try {
        const returnData = await fetch(`${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}/groups/all/`, {
            method: 'GET',
            headers: {
                'Authorization': token,
                'X-Forwarded-For': ip,
            }
        })
            .then(response => response.json())
            .then((response) => {
                if(response.status) {
                    res.status(200).json(response);
                } else{
                    // console.log('get all groups fail', response);
                    res.status(400).json({ message: '取得所有機關資料失敗' });
                }
            })
            .catch((err) => {
                res.status(400).json((err));
            });
        return returnData;
    } catch (err) {
        return res.status(500).json(err);
    }
}