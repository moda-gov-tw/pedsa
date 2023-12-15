import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import axiosPlus from 'sections/api/axiosPlus';
import useClock from 'hooks/useClock';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
    Box,
    Button,
    Divider,
    Grid,
    Stack,
    InputLabel,
    TextField,
    Typography,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import RefreshIcon from '@mui/icons-material/Refresh';

// third-party
import axios from 'axios';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import ProjectStepper from 'sections/apps/progress/project_stepper';
import GeneralStepper from 'sections/apps/progress/general-stepper';
import NoNumberStepper from 'sections/apps/progress/no-number-stepper';
import StatusButton from "../../../sections/apps/data-connect/status-button";
import DownloadFiles from "../../../sections/apps/data-connect/download-files";
import { mockPESelections } from '../../../utils/mock-privacy-enhancement-selections';
import petsLog from 'sections/apps/logger/insert-system-log';
import useUser from 'hooks/useUser';

/*********** 
 * Control * 
 ***********/

// 
const mapSystemName2QueryIDName = {
    "KAnonymous": "k_project_id",
    "syntheticData": "syn_project_id",
    "differentialPrivacy": "dp_project_id",
};

// API: fetch project status (/api/projects/status)
const handleFetchProjectStatus = async (session, project_id, setProjectStatus) => {
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`,
        },
        params: {
            project_id: project_id,
        },
    };
    const promiseResult = await axiosPlus({
        method: "GET",
        stateArray: null,
        url: "/api/project/get_projectStatus",
        config: config,
        showSuccessMsg: false,
    });

    if (promiseResult && promiseResult?.status == 200)
        setProjectStatus(promiseResult.data.obj.status);
}

// API: set new project status (/api/project/put_projectStatus)
const handleSetProjectStatus = async (session, project_id, newStatus) => {
    const payload = {
        project_id: project_id,
        status: newStatus,
    };
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
    };
    axiosPlus({
        method: "PUT",
        stateArray: null,
        url: "/api/project/put_projectStatus",
        payload: payload,
        config: config,
        showSuccessMsg: false,
    });
}

// API: fetch sub-system status (/api/project/get_?_checkstatus)
const handleFetchSubSystemStatus = async (session, projectDetail, url) => {
    const config = {
        headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
        params: {
            project_name: projectDetail.project_eng,
            loginname: session.tocken.account,
            returnurl: window.location.href,
        },
    }

    const promiseResult = await axiosPlus({
        method: "GET",
        stateArray: null,
        url: url,
        config: config,
        showSuccessMsg: false,
    })

    if (promiseResult && promiseResult?.status == 200)
        return promiseResult?.data[0];
}

// API: request sub-system connect (/api/project/get_?_conn)
const handleSubSystemConn = async (session, projectDetail, url) => {
    const config = {
        headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
        params: {
            project_name: projectDetail.project_eng,
            filename: projectDetail.jointablename,
        },
    }

    const promiseResult = await axiosPlus({
        method: "GET",
        stateArray: null,
        url: url,
        config: config,
        showSuccessMsg: false,
    })

    return promiseResult.data[0].obj;
}

const requestSystemInfo2 = async (session, projectDetail, innerCheckStatusURL, innerConnURL) => {
    const checkStatusPromiseResult = await handleFetchSubSystemStatus(session, projectDetail, innerCheckStatusURL)
    try {
        if (checkStatusPromiseResult.status == 1) {
            // 子系統 checkstatus API 回傳 status = 1 表示系統已建立，func return 詳細資料
            // console.log("checkStatusPromiseResult:", checkStatusPromiseResult);
            return { status: 1, obj: checkStatusPromiseResult.obj };
        }
        else if (checkStatusPromiseResult.status == 0) {
            // 子系統 checkstatus API 回傳 status = 0 表示系統未建立此專案，func return 詳細資料

            // --- [Abandoned] Call subsystem conn api to create project. Now, this will be Tony to call  --- //
            // const connPromiseResult = await handleSubSystemConn(session, projectDetail, innerConnURL)      //
            // console.log("connPromiseResult:", connPromiseResult);                                          //
            // ---------------------------------------------------------------------------------------------- //

            return { status: 0, obj: null };
        }
        else
            throw { status: 500, message: "[Custom] Unexpected error occurred", response: checkStatusPromiseResult };
    }
    catch (error) {
        console.log("[Error]\n", error);
        // console.log(`[Request Error]\n status:\n ${error?.response?.status}\nstatusText:\n ${error?.response?.statusText}`);
        return { status: 500, obj: null };
    }
}

// API: fetch project detail (/api/projects/detail)
const handleFetchProjectDetail = async (session, project_id, [projectDetail, setProjectDetail]) => {
    const payload = {
        project_id: project_id,
    };
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
    };
    axiosPlus({
        method: "POST",
        stateArray: [projectDetail, setProjectDetail],
        url: "/api/project/post_projectDetail",
        payload: payload,
        config: config,
        showSuccessMsg: false,
    })
        .then((response) => {
            // console.log("projectDetail:", response);
        })
}

// API: reset sub-system status (/api/project/get_?_reset)
const handleReset = async (session, systemName, projectDetail, subsystemProjectID, url,) => {
    const requestProps = {
        method: "GET",
        stateArray: null,
        url: url,
        config: {
            headers: {
                Authorization: `Bearer ${session.tocken.loginUserToken}`,
            },
            params: { project_name: projectDetail.project_eng, },
        },
        showSuccessMsg: false,
    }
    requestProps.config.params[mapSystemName2QueryIDName[systemName]] = subsystemProjectID;
    console.log("Reset requestProps", requestProps);

    const promiseResult = await axiosPlus(requestProps);
    console.log("Reset promise", promiseResult);
}


/****************  
 * View-control * 
 ****************/
const PrivacyEnhancement = () => {
    const router = useRouter();
    const { data: session } = useSession();
    const user = useUser();
    const [clockCount] = useClock({ delay: 5 * 1000, restartState: 0, finalState: 3, increaseStep: 1 }); // Automatic counter, increases by 1 every 5 seconds.

    const [project_id, setProject_id] = useState(null);
    const [project_name, setProject_name] = useState(null);
    const [projectEngName, setProjectEngName] = useState(null);
    const [gotQuery, setGotQuery] = useState(false);

    const [projectStatus, setProjectStatus] = useState(-1);
    const [loading, setLoading] = useState(true);
    const [projectDetail, setProjectDetail] = useState(null);
    const [subsystemInfos_K, setSubsystemInfos_K] = useState({});
    const [subsystemInfos_GAN, setSubsystemInfos_GAN] = useState({});
    const [subsystemInfos_DP, setSubsystemInfos_DP] = useState({});

    const [gotStatusK, setGotStatusK] = useState(false);
    const [gotStatusGan, setGotStatusGan] = useState(false);
    const [gotStatusDP, setGotStatusDP] = useState(true); // [TODO-DP] -> false init

    const [preprocessedData, setPreprocessedData] = useState(null);
    const [systemID2Name, setSystemID2Name] = useState(null);
    const [systemID2StatusLabelObject, setSystemID2StatusLabelObject] = useState(null);
    const [oneCanDownload, setOneCanDownload] = useState(false);
    const [wroteLog, setWroteLog] = useState({});

    // Mounting effect
    useEffect(() => {
        // Get project_id, project_name
        const _project_id = router.query.project_id;
        setProject_id(_project_id);

        // Fetch API /projects/detail
        handleFetchProjectDetail(session, _project_id, [projectDetail, setProjectDetail]);

        // Mapping of sub-systemID to name
        setSystemID2Name({
            "KAnonymous": "K匿名處理",
            "syntheticData": "合成資料處理",
            "differentialPrivacy": "差分隱私處理",
        });

        setGotQuery(true);
    }, []);

    // After mount effect
    // useEffect(() => {
    //     if (project_id) {

    //     }
    // }, [gotQuery]);

    // Periodic effect (refresh depends on clock)
    useEffect(() => {
        // console.log(clockCount);
        if (project_id) {
            // Update project status
            handleFetchProjectStatus(session, project_id, setProjectStatus);
        }

        if (projectDetail) {
            // syslog enter this page
            if (!wroteLog["enterPage"]) {
                petsLog(session, 0, `Login User ${user.account} 進入隱私機制強化選擇`, projectDetail.project_name);
                setWroteLog(prev => ({ ...prev, ["enterPage"]: true }));
            }

            // Save projectName projectEngName
            setProject_name(projectDetail.project_name);
            setProjectEngName(projectDetail.project_eng);

            // Update sub-system status
            // K
            requestSystemInfo2(session, projectDetail, "/api/project/get_k_checkstatus", "/api/project/get_k_conn")
                .then((response) => {
                    console.log("K response:", response);
                    if (response.status == 1) {
                        setSubsystemInfos_K(response);
                        setGotStatusK(true);
                    }

                    // join 結束、conn 成功，但中途子系統發生錯誤
                    if (gotStatusK) {
                        // 目前邏輯是子系統都已建立專案才可顯示子系統選擇畫面，因此要維持 gotStatus = true。
                        if (response.status == 0) {
                            // 專案不明原因消失
                            setSubsystemInfos_K((prev) => ({ ...prev, ["project_status"]: "-100", ["return_url"]: "" }));
                        }
                        if (response.status == 500) {
                            // 其他類型錯誤
                            setSubsystemInfos_K((prev) => ({ ...prev, ["project_status"]: "-500", ["return_url"]: "" }));
                        }
                    }
                });
            // GAN
            requestSystemInfo2(session, projectDetail, "/api/project/get_syn_checkstatus", "/api/project/get_syn_conn")
                .then((response) => {
                    console.log("SYN response:", response);
                    if (response.status == 1) {
                        setSubsystemInfos_GAN(response);
                        setGotStatusGan(true);
                    }

                    // join 結束、conn 成功，但中途子系統發生錯誤
                    if (gotStatusK) {
                        // 目前邏輯是子系統都已建立專案才可顯示子系統選擇畫面，因此要維持 gotStatus = true。
                        if (response.status == 0) {
                            // 專案不明原因消失
                            setSubsystemInfos_GAN((prev) => ({ ...prev, ["project_status"]: "-100", ["return_url"]: "" }));
                        }
                        if (response.status == 500) {
                            // 其他類型錯誤
                            setSubsystemInfos_GAN((prev) => ({ ...prev, ["project_status"]: "-500", ["return_url"]: "" }));
                        }
                    }
                });
            // DP
            requestSystemInfo2(session, projectDetail, "/api/project/get_dp_checkstatus", "/api/project/get_dp_conn")
                .then((response) => {
                    console.log("DP response:", response);
                    if (response.status == 1) {
                        setSubsystemInfos_DP(response);
                        setGotStatusDP(true);
                    }

                    // join 結束、conn 成功，但中途子系統發生錯誤
                    if (gotStatusK) {
                        // 目前邏輯是子系統都已建立專案才可顯示子系統選擇畫面，因此要維持 gotStatus = true。
                        if (response.status == 0) {
                            // 專案不明原因消失
                            setSubsystemInfos_DP((prev) => ({ ...prev, ["project_status"]: "-100", ["return_url"]: "" }));
                        }
                        if (response.status == 500) {
                            // 其他類型錯誤
                            setSubsystemInfos_DP((prev) => ({ ...prev, ["project_status"]: "-500", ["return_url"]: "" }));
                        }
                    }
                });
        }
    }, [clockCount, gotQuery, projectDetail])

    // Preprocess data
    useEffect(() => {
        // Create status dictionary of sub-systems
        const generalFailStatus = "系統處理中";
        const projectNoFoundStatus = "錯誤: 專案未建立";
        const unexpextErrorStatus = "不明原因錯誤";
        const subSystemInitStatus = "資料已就緒";
        const ganSystemFailStatus = "資料合成失敗";
        const systemID2StatusList = {
            "KAnonymous": ["可進行概化規則設定", "可進行隱私強化處理", "隱私強化處理中", "可進行資料匯出", "資料匯出中", "可下載強化資料"],
            "syntheticData": ["資料合成中", "可進行感興趣欄位設定", "可用性分析中", "可進行資料匯出", "資料匯出中", "可下載強化資料"],
            "differentialPrivacy": ["資料處理中", "可進行關聯欄位設定", "差分隱私處理中", "可下載強化資料"], // [TODO-DP] This is not the status list of DP
        }

        // === stepper label name mapping table === //
        const newObject = {}
        const listToObject = (list) => list.reduce((obj, item, index) => ({ ...obj, [index]: item }), {});
        for (let key_systemID in systemID2StatusList) {
            newObject[key_systemID] = listToObject(systemID2StatusList[key_systemID]);
            newObject[key_systemID][-1] = subSystemInitStatus; // 顯示資料已就緒的起始狀態
            newObject[key_systemID][-2] = ganSystemFailStatus; // 使用者操作失誤，引導使用者進入子系統重新設定, [Notice] current only GAN has fail status (99: 合成失敗)
            newObject[key_systemID][-100] = projectNoFoundStatus; // 專案不明原因消失、未建立、遭刪除
            newObject[key_systemID][-500] = unexpextErrorStatus; // 其他類型錯誤
            newObject[key_systemID][-999] = generalFailStatus; // 通用型錯誤: 子系統正常或不正常處理，卻未告知前端的特殊例外狀態
        }
        // console.log("newObject", newObject);
        setSystemID2StatusLabelObject(newObject);
        // ================================= //

        // mappingTable of "subsystem backend status to frontens status"
        const [readyStatusK, readyStatusGan, readyStatusDP] = [3, 2, 2];
        // K
        // sub-project status map to stepper label name
        const mappingStatusNameTableK = [
            { range: [0, readyStatusK], newState: -1 },
            { range: [4, 5], newState: 0 },
            { range: [6, 6], newState: 1 },
            { range: [7, 8], newState: 2 },
            { range: [9, 9], newState: 3 },
            { range: [10, 10], newState: 4 },
            { range: [11, 11], newState: 5 },
        ];
        // sub-project status map to stepper circle status
        const mappingStatusStepperTableK = [
            { range: [-1, readyStatusK], newState: -1 },
            { range: [4, 5], newState: 0 },
            { range: [6, 6], newState: 1 },
            { range: [7, 10], newState: 2 },
            { range: [11, 11], newState: 3 },
        ];
        // GAN
        // sub-project status map to stepper label name
        const mappingStatusNameTableGan = [
            { range: [0, readyStatusGan], newState: -1 },
            { range: [3, 3], newState: 0 },
            { range: [4, 4], newState: 1 },
            { range: [5, 5], newState: 2 },
            { range: [6, 6], newState: 3 },
            { range: [7, 7], newState: 4 },
            { range: [8, 8], newState: 5 },
        ];
        // sub-project status map to stepper circle status
        const mappingStatusStepperTableGan = [
            { range: [-1, readyStatusGan], newState: -1 },
            // { range: [, ], newState: 0 },
            { range: [3, 3], newState: 1 },
            { range: [4, 4], newState: 2 },
            { range: [5, 7], newState: 3 },
            { range: [8, 8], newState: 4 },
        ];
        // DP
        // [TODO-DP] Need to define the real DP mapping table
        // sub-project status map to stepper label name
        const mappingStatusNameTableDP = [
            { range: [0, readyStatusDP], newState: -1 },
            { range: [3, 3], newState: 0 }, // 顯示文字: 資料處理中
            { range: [4, 4], newState: 1 }, // 顯示文字: 可進行關聯欄位設定
            { range: [5, 5], newState: 2 }, // 顯示文字: 差分隱私處理中
            { range: [6, 6], newState: 3 }, // 顯示文字: 可載檔案與查看報表
        ];
        // sub-project status map to stepper circle status
        const mappingStatusStepperTableDP = [
            { range: [-1, readyStatusDP], newState: -1 }, // 匯入 ~ 就緒
            { range: [3, 3], newState: 0 }, // (1) 資料處理中
            { range: [4, 4], newState: 1 }, // (2) 可進行關聯欄位設定
            { range: [5, 5], newState: 2 }, // (3) 差分隱私處理中
            { range: [6, 6], newState: 3 }, // (4) 可載檔案與查看報表
        ];

        // ***************************************** //
        // Binary Search to address interval mapping //
        // ***************************************** //
        // stepper label name transform
        function mapStateToNewLabelState(status, mappingTable, systemName) {
            // Example of mappingTable //
            // const mappingTable = [
            //     { range: [1, 3], newState: 1 },
            //     { range: [4, 8], newState: 2 },
            //     // Add more ranges and new status here
            // ];

            // 錯誤 專案未建立或消失
            if (status == -100)
                return -100;

            // API checkstatus request error or other unexpexted main-system error
            if (status == -500)
                return -500;

            // 資料合成失敗時的特殊顯示 (應顯示燈號 1 (index 0)，並允許使用者點選前往子系統修改設定)
            if (systemName == "syntheticData") // [TODO-DP] k & dp 是否有這種重設狀態? 待確認
                if (status == 99)
                    return -2;

            // Binary Search
            let left = 0;
            let right = mappingTable.length - 1;

            while (left <= right) {
                const mid = Math.floor((left + right) / 2);
                const { range, newState } = mappingTable[mid];

                if (status >= range[0] && status <= range[1]) {
                    return newState;
                } else if (status < range[0]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            }

            // Out of range: special cases
            return -999; // 後端未告知的正常或不正常處理狀態
        }

        // stepper circle status transform
        function mapStateToNewStepperState(status, mappingTable, systemName) {
            // Example of mappingTable //
            // const mappingTable = [
            //     { range: [1, 3], newState: 1 },
            //     { range: [4, 8], newState: 2 },
            //     // Add more ranges and new status here
            // ];

            // 錯誤 專案未建立或消失
            if (status == -100)
                return -1;

            // API checkstatus request error or other unexpexted main-system error
            if (status == -500)
                return -1;

            // 資料合成失敗時的特殊顯示 (應顯示燈號 1 (index 0)，並允許使用者點選前往子系統修改設定)
            if (systemName == "syntheticData")
                if (status == 99)
                    return 0;

            // Binary Search
            let left = 0;
            let right = mappingTable.length - 1;

            while (left <= right) {
                const mid = Math.floor((left + right) / 2);
                const { range, newState } = mappingTable[mid];

                if (status >= range[0] && status <= range[1]) {
                    return newState;
                } else if (status < range[0]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            }

            // Out of range: special cases
            return -1; // Return -1 if the status is not in any range
        }
        // ***************************************** //


        if (gotStatusK & gotStatusGan & gotStatusDP) {
            const loginname = session.tocken.account;
            const returnurl = window.location.href;
            var rawData = {
                "KAnonymous": {
                    'originStatus': subsystemInfos_K.project_status, // backend status
                    'readyStatus': readyStatusK, // backend ready status
                    'labelStatus': mapStateToNewLabelState(subsystemInfos_K.project_status, mappingStatusNameTableK), // frontend label status
                    'stepperStatus': mapStateToNewStepperState(subsystemInfos_K.project_status, mappingStatusStepperTableK), // frontend stepper current status
                    'maxStatus': Object.keys(mappingStatusStepperTableK).length - 2, // frontend final stepper status (-2 cuz zero-indexing & -1 status)
                    'statusNameList': systemID2StatusList.KAnonymous,
                    'subsystemProjectID': subsystemInfos_K.project_id,
                    'url': (subsystemInfos_K.return_url == "" || subsystemInfos_K.return_url == undefined || subsystemInfos_K.return_url == null) ? "" : `${subsystemInfos_K.return_url}&loginname=${loginname}&returnurl=${returnurl}`,
                    'links': {
                        'decrypt': '/apps/project/data-decrypt',
                        'reset': '/api/project/get_k_reset',
                    }
                },
                "syntheticData": {
                    'originStatus': subsystemInfos_GAN.project_status, // backend status
                    'readyStatus': readyStatusGan, // backend ready status
                    'labelStatus': mapStateToNewLabelState(subsystemInfos_GAN.project_status, mappingStatusNameTableGan), // frontend label status
                    'stepperStatus': mapStateToNewStepperState(subsystemInfos_GAN.project_status, mappingStatusStepperTableGan), // frontend stepper current status
                    'maxStatus': Object.keys(mappingStatusStepperTableGan).length - 2, // frontend final stepper status (-2 cuz zero-indexing & -1 status)
                    'statusNameList': systemID2StatusList.syntheticData,
                    'subsystemProjectID': subsystemInfos_GAN.project_id,
                    'url': (subsystemInfos_GAN.return_url == "" || subsystemInfos_GAN.return_url == undefined || subsystemInfos_GAN.return_url == null) ? "" : `${subsystemInfos_GAN.return_url}&loginname=${loginname}&returnurl=${returnurl}`,
                    'links': { 'reset': '/api/project/get_syn_reset' }
                },
                "differentialPrivacy": {
                    'originStatus': subsystemInfos_DP.project_status, // backend status
                    'readyStatus': readyStatusDP, // backend ready status
                    'labelStatus': mapStateToNewLabelState(subsystemInfos_DP.project_status, mappingStatusNameTableDP), // frontend label status
                    'stepperStatus': mapStateToNewStepperState(subsystemInfos_DP.project_status, mappingStatusStepperTableDP), // frontend stepper current status
                    'maxStatus': Object.keys(mappingStatusStepperTableDP).length - 2, // frontend final stepper status (-2 cuz zero-indexing & -1 status)
                    'statusNameList': systemID2StatusList.differentialPrivacy,
                    'subsystemProjectID': subsystemInfos_DP.project_id,
                    'url': (subsystemInfos_DP.return_url == "" || subsystemInfos_DP.return_url == undefined || subsystemInfos_DP.return_url == null) ? "" : `${subsystemInfos_DP.return_url}&loginname=${loginname}&returnurl=${returnurl}`,
                    'links': { 'reset': '/api/project/get_dp_reset' }
                },
            }

            // Control the buttons showing condition
            const preprocessedAPI = (api_obj) => {
                const isFinalStausObject = { "KAnonymous": false, "syntheticData": false, "differentialPrivacy": false };
                for (const key_systemID in api_obj) {
                    let system = api_obj[key_systemID];
                    let linksArray = [];

                    const isFinalStatus = (Number(system.stepperStatus) == Number(system.maxStatus)) ? true : false;
                    isFinalStausObject[key_systemID] = isFinalStatus;
                    // console.log("FINAL:", [key_systemID, isFinalStatus, system.stepperStatus, system.maxStatus]);
                    // Change project status when one system can download file
                    if (!oneCanDownload) {
                        if (isFinalStatus) {
                            if (-1 < projectStatus && projectStatus <= 5) {
                                handleSetProjectStatus(session, project_id, 6);
                                setOneCanDownload(true);
                            }
                            else if (projectStatus > 5)
                                setOneCanDownload(true);
                        }
                    }

                    // Button: download dataset 
                    if (key_systemID == "differentialPrivacy") {
                        linksArray.push({
                            'button_name': "下載資料集",
                            'file_name': "file", /* [TODO-DP] Need to change to real DP download filename */
                            'url': "", /* [TODO-DP] Need to change to real DP download link */
                            'icon': <DescriptionOutlinedIcon />,
                            'behavior': 'download',
                            'clickFunc': null,
                            'disabled': true, // (isFinalStatus) ? false : true, [TODO-DP] 
                        });
                    }
                    else {
                        const routerConfigDownloadButton = {
                            pathname: "/apps/project/data-download",
                            query: {
                                project_id: project_id,
                                project_name: project_name,
                                project_eng_name: projectEngName,
                                system_name: key_systemID,
                                sub_system_id: system.subsystemProjectID,
                            },
                        }
                        linksArray.push({
                            'button_name': "下載資料集",
                            'file_name': "",
                            'url': "",
                            'icon': <DownloadIcon />,
                            'behavior': 'exeClickFunc',
                            'clickFunc': () => {
                                router.push(routerConfigDownloadButton);
                            },
                            'disabled': (isFinalStatus) ? false : true,
                        })
                    }

                    // Button: check report
                    if (key_systemID == "differentialPrivacy") {
                        // const routerConfigReportButton = {
                        //     pathname: "/apps/project/data-report",
                        //     query: {
                        //         project_id: project_id,
                        //         project_name: project_name,
                        //         system_name: key_systemID,
                        //         sub_system_id: system.subsystemProjectID,
                        //     },
                        // }
                        // linksArray.push({
                        //     'button_name': "查看報表",
                        //     'file_name': "",
                        //     'url': "",
                        //     'icon': <DescriptionOutlinedIcon />,
                        //     'behavior': 'exeClickFunc',
                        //     'clickFunc': () => {
                        //         router.push(routerConfigReportButton);
                        //     },
                        //     'disabled': (isFinalStatus) ? false : true,
                        // });

                        linksArray.push({
                            'button_name': "查看報表",
                            'file_name': "",
                            'url': "", /* [TODO-DP] Need to change to real DP url */
                            'icon': <DescriptionOutlinedIcon />,
                            'behavior': 'href',
                            'clickFunc': null,
                            'disabled': true, // (isFinalStatus) ? false : true, // [TODO-DP] 
                        });
                    }
                    else {
                        const routerConfigReportButton = {
                            pathname: "/apps/project/data-report",
                            query: {
                                project_id: project_id,
                                project_name: project_name,
                                system_name: key_systemID,
                                sub_system_id: system.subsystemProjectID,
                            },
                        }
                        linksArray.push({
                            'button_name': "查看報表",
                            'file_name': "",
                            'url': "",
                            'icon': <DescriptionOutlinedIcon />,
                            'behavior': 'exeClickFunc',
                            'clickFunc': () => {
                                router.push(routerConfigReportButton);
                            },
                            'disabled': (isFinalStatus) ? false : true,
                        });
                    }

                    // Button: data decrypt
                    const routerConfigDecryptButton = {
                        pathname: system.links.decrypt,
                        query: {
                            project_id: project_id,
                            project_name: project_name,
                            system_name: key_systemID,
                            sub_system_id: system.subsystemProjectID,
                        },
                    }
                    if (system.links.decrypt) {
                        linksArray.push({
                            'button_name': "資料解密",
                            'file_name': "",
                            'url': "",
                            'icon': <LockOpenIcon sx={{ transform: 'scaleX(-1)' }} />,
                            'behavior': 'exeClickFunc',
                            'clickFunc': () => {
                                router.push(routerConfigDecryptButton);
                            },
                            'disabled': (isFinalStatus) ? false : true,
                        })
                    }

                    // Button: reset
                    if (system.links.reset) {
                        linksArray.push({
                            'button_name': `重新執行${systemID2Name[key_systemID]}`,
                            'file_name': "",
                            'url': "",
                            'icon': <RefreshIcon sx={{ transform: 'scaleX(-1)' }} />,
                            'behavior': 'exeClickFunc',
                            'clickFunc': () => { handleReset(session, key_systemID, projectDetail, system.subsystemProjectID, system.links.reset) },
                            'disabled': (Number(system.labelStatus) > -1) ? false : true,
                        })
                        system.linksArray = linksArray;
                    }
                }

                // No one can download
                if (isFinalStausObject.KAnonymous == false && isFinalStausObject.syntheticData == false && isFinalStausObject.differentialPrivacy == false) {
                    handleSetProjectStatus(session, project_id, 5);
                    setOneCanDownload(false);
                }

                // console.log("linksArray:", api_obj);
                return api_obj;
            }

            setPreprocessedData(preprocessedAPI(rawData));
            setLoading(false);
        }
    }, [subsystemInfos_K, subsystemInfos_GAN, subsystemInfos_DP])

    const handleClickBlockButton = (event, url) => {
        if (-1 < projectStatus && projectStatus <= 4)
            handleSetProjectStatus(session, project_id, 5);
        window.location.href = url;
    }

    /******** 
     * View * 
     ********/
    return (
        <Page title="Customer List">
            {/* 頂部進度條 */}
            <Box sx={{ width: '100%', mb: "20px", mt: "50px", ml: "50px", alignItems: "center" }} >
                <Box sx={{ width: "60%", alignItems: "center" }} >
                    <ProjectStepper currentStep={projectStatus} terminatedStep={null} />
                </Box>
            </Box>

            <Box sx={{ width: '100%', mb: "20px", mt: "50px" }}>
                <Grid container spacing={6} sx={{ ml: "50px" }}>
                    <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>

                        {/* Page title */}
                        <Grid container item>
                            <Typography variant='h3'>隱私強化機制選擇</Typography>
                        </Grid>

                        <Divider />

                        <Grid container item spacing={3}>
                            <Grid container spacing={12} >
                                <Grid item lg={2}>
                                    <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案名稱</InputLabel>
                                </Grid>
                                <Grid item lg={8}>
                                    <TextField
                                        fullWidth
                                        value={project_name}
                                        InputProps={{ readOnly: true, }}
                                        disabled
                                        color="secondary"
                                    />
                                </Grid>
                            </Grid>
                        </Grid>

                        <Stack direction="row" spacing={1} sx={{ minWidth: '100%' }}>
                            {(loading) ? "" /*loading*/ :
                                <>
                                    {
                                        Object.keys(preprocessedData).map((key_systemID, index) => {
                                            const system = preprocessedData[key_systemID];
                                            console.log(key_systemID, system.url);
                                            return (
                                                <Stack direction="column" spacing={1} sx={{ minWidth: '33%' }}>
                                                    {/* Block Button */}
                                                    {(system.url == "") ?
                                                        <StatusButton currentStatus={-1} triggrtStatus={Number(system.readyStatus)} buttonName={systemID2Name[key_systemID]} minHeight={"33%"} /> :
                                                        <StatusButton currentStatus={Number(system.originStatus)} triggrtStatus={Number(system.readyStatus)} buttonName={systemID2Name[key_systemID]} minHeight={"33%"} onClickFunc={(e) => { handleClickBlockButton(e, system.url) }} />
                                                    }

                                                    {/* Stepper */}
                                                    <GeneralStepper currentStep={Number(system.stepperStatus)} terminatedStep={Number(system.maxStatus) + 1} StepName={systemID2StatusLabelObject[key_systemID][system.labelStatus]} />

                                                    {/* More button */}
                                                    <DownloadFiles height={400} argArray={system.linksArray} listItemComponent="div" />
                                                </Stack>
                                            )
                                        })
                                    }
                                </>
                            }
                        </Stack>
                    </Stack>
                </Grid>
            </Box>

            {/* bottom button */}
            <Box
                m={1}
                display="flex"
                justifyContent="flex-end"
                alignItems="flex-end"
            >
                <Button
                    variant="contained"
                    onClick={() => {
                        router.push('/apps/project/projects-table');
                    }}
                >
                    回到專案列表
                </Button>
            </Box>
        </Page>
    )
}

PrivacyEnhancement.getLayout = function getLayout(page) {
    return <Layout>{page}</Layout>;
};

export default PrivacyEnhancement;