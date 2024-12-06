// ==============================|| PROJECT - GET CONTAINERS STATUS  ||============================== //

import axios from 'axios';
export default async function handler(req, res) {
  // http url
  const api_path = '/sys/permssion_compare';
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
    // console.log('response', response);
    return res.status(response.status).json(response.data);
  } catch (error) {
    // console.log('Error\n', error);
    return res.status(error.status).json(error);
  }
}
