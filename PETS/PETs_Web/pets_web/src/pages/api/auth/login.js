import Qs from 'qs';

// ==============================|| ACCOUNT - LOGIN  ||============================== //

export default async function handler(req, res) {
    try {
        let details = Qs.stringify(req.body);
        const returnData = await fetch(`${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}/login/`, {
            method: 'POST',
            body: details,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'accept': 'application/json'
            }
        })
            .then(response => response.json())
            .then((response) => {
                if(response.status) {
                    response.obj.account_name = req.body.account;
                    res.status(200).json(response);
                } else{
                    console.log('login fail');
                    res.status(400).json({ message: '帳號或是密碼錯誤' });
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
// 只有network error會到catch