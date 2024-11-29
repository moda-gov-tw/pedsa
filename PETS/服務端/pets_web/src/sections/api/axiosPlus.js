// next
import { signOut } from 'next-auth/react';

// third-party
import axios from 'axios';

/**
 * Function: axiosPlus
 *
 * Sends an internal HTTP GET/POST/PUT request using the `axios()` method.
 *
 * @param {object} prop
 * @param {string} prop.method
 * - The http request method (GET/POST/PUT).
 * @param {Array | null} prop.stateArray
 * - The stateArray of useState.
 * @param {string} prop.url
 * - The request URL.
 * @param {object} prop.payload
 * - (Option) The request payload.
 * @param {object} prop.config
 * - The request configuration.
 * @param {boolean} [prop.showSuccessMsg=true]
 * - Showing response and result on console when request successfully.
 * @returns {any} Response.
 */
export default async function axiosPlus({
  method = '',
  stateArray = [state, setState],
  url = '',
  payload = {},
  config = {},
  showSuccessMsg = true,
  showErrorMsg = false
}) {
  // Define a async function to send http request
  try {
    // Switch GET/POST/PUT
    var promiseResult = null;
    if (method == 'GET') promiseResult = await axios.get(url, config);
    else if (method == 'POST') promiseResult = await axios.post(url, payload, config);
    else if (method == 'PUT') promiseResult = await axios.put(url, payload, config);
    const response = promiseResult;
    // console.log('response', response);

    // 接停權錯誤訊息，如果被停權則登出
    if (response.status === 200 && response.data.msg) {
      if (response.data.msg === 'User has been suspended.') {
        localStorage.clear();
        signOut({ redirect: false });
      }
    }

    //if (response.status == 200 && response.statusText == 'OK') {
    if (response.status == 200 ) {
      // if (showSuccessMsg) console.log('[AxiosPlus] Success, response.data.obj:\n', response.data.obj);

      // Update the state of response data
      if (stateArray) {
        const [state, setState] = stateArray;
        setState(response.data.obj);
      }

      return response;
    } // Throw a self-defined unexpected error
    else throw { status: 500, message: '[AxiosPlus] Unexpected error occurred', response: response };
  } catch (error) {
    // console.log('axiosPlus error', error);
    // Unexpected error
    if (error.status == 500) {
      // if (showErrorMsg) console.log('[AxiosPlus] Unexpected Error\n', error);
    }
    // HTTP status codes in IIS (Internet Information Services)
    else {
      // if (showErrorMsg) console.log('[AxiosPlus] Error\n', error);
    }
    return error;
  }
}
