// ==============================|| PROJECT - GET LIST  ||============================== //

import axios from 'axios';
export default async function handler(req, res) {
  // http url
  const api_path = '/projects/list';
  const url = `${process.env.PERMISSION_SERVICE}:${process.env.PERMISSION_SERVICE_PORT}${api_path}`;
  // http config
  const token = req.headers['authorization'];
  const ip = req.headers['x-real-ip'] || req.connection.remoteAddress;
  const config = {
    headers: {
      accept: 'application/json',
      Authorization: token,
      'X-Forwarded-For': ip
    }
  };

  // send axios http request
  try {
    const response = await axios.get(url, config);
    return res.status(response.status).json(response.data);
  } catch (error) {
    // console.log('Error\n', error);
    // 被停權
    if (error.response.data.msg === 'User has been suspended.') {
      res.status(200).json(error.response.data);
    }
    return res.status(error.response.status).json(error);
  }
}
