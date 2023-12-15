import axiosPlus from "sections/api/axiosPlus";

/**
 * Function: petsLog
 *
 * [API] Send post request to insert system log to Pets' database.
 *
 * @param {any} session
 * - (Require) The session of {data: session} from useSession.
 * @param {Number} logType
 * - (Require) -1: DEBUG (除錯), 0: INFO (訊息), 1: WARNING (警告), 2: ERROR (錯誤)
 * @param {String} logContent
 * - (Require) The log string will be inserted.
 * @param {String} projectName
 * - (Option) `project_name` at project related page.
 * @param {String} isServerSide
 * - is isServerSide
 * @returns {Object} Format: {status: Boolean, obj: Object, msg: String}.
 * If status is true, obj is the payload request to API server. Otherwise, an error has occurred.
 */
export default async function petsLog(session, logType, logContent, projectName, isServerSide = false) {
    const logTypeTable = {
        '-1': 'DEBUG', //  (除錯) 
        '0': 'INFO', //    (訊息) 
        '1': 'WARNING', // (警告)
        '2': 'ERROR', //   (錯誤)
    }
    var assert = require('assert');
    assert(logTypeTable[logType], "logType should be number of -1: DEBUG (除錯), 0: INFO (訊息), 1: WARNING (警告), 2: ERROR (錯誤).");

    const payload = {
        useraccount: session.tocken.account,
        log_type: logTypeTable[logType],
        logcontent: logContent,
    };

    if (projectName)
        payload['project_name'] = projectName;

    const config = {
        headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
    };

    const promiseResult = await axiosPlus({
        method: "POST",
        stateArray: null,
        url: (isServerSide) ? `${process.env.NEXTAUTH_URL}/api/sys/post_sysInsert` : '/api/sys/post_sysInsert',
        payload: payload,
        config: config,
        showSuccessMsg: false,
    });

    if (promiseResult.status == 200) {
        if (promiseResult.data.status == false)
            console.log("錯誤: 系統紀錄寫入失敗", promiseResult.data);
        return promiseResult.data; // promiseResult.data = {status: true/false, obj: {}, msg: ""};
    }
    else {
        // if http fail
        console.log("錯誤: 系統紀錄寫入失敗", promiseResult);
        return { status: false, obj: promiseResult, msg: "錯誤: 系統紀錄寫入失敗" };
    }
}