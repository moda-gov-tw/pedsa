import Qs from 'qs';

// ==============================|| ACCOUNT - LOGIN  ||============================== //

export default async function handler(req, res) {
    res.setHeader("Content-Security-Policy", "default-src 'self'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;");
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
                    // console.log('login fail', response);
                    if(response.msg.includes('member is inactive')){
                        res.status(400).json({ message: '此帳號目前已被停權' });
                    }
                    else if(response.msg.includes('no member exist')) {
                        res.status(400).json({message: '此帳號不存在，請確認帳號'});
                    }
                    else if(response.msg.includes('account or password wrong')) {
                        res.status(400).json({message: '帳號或是密碼錯誤'});
                    }
                    else{
                        res.status(400).json({message: '登入失敗，請洽管理員'});
                    }
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