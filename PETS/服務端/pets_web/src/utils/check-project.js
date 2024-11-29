import axios from 'axios';

export async function checkProjectEng(project_eng, config, setCheckPopUp, setPopUpMsg) {
  let msg = '';
  if (project_eng && project_eng !== '') {
    const url = '/api/project/post_checkProjectEng';
    const payload = { project_eng: project_eng };
    await axios.post(url, payload, config).then((response) => {
      if (response.data.status) {
        msg = 'ok';
      }
      if (response.data.status === false) {
        msg = '專案資料夾名稱已被使用，請更換專案資料夾名稱';
        setPopUpMsg(msg);
        setCheckPopUp(true);
      }
    });
  }
  return msg;
}

export async function checkProjectName(project_name, config, setCheckPopUp, setPopUpMsg) {
  let msg = '';
  if (project_name && project_name !== '') {
    const url = '/api/project/post_checkProjectCht';
    const payload = { project_name: project_name };
    await axios.post(url, payload, config).then((response) => {
      if (response.data.status) {
        msg = 'ok';
      }
      if (response.data.status === false) {
        msg = '專案名稱已被使用，請更換專案名稱';
        setPopUpMsg(msg);
        setCheckPopUp(true);
      }
    });
  }
  return msg;
}

export function checkEmpty(project_name, project_eng, setCheckPopUp, setPopUpMsg) {
  let msg = '';
  if (!project_name || project_name === '' || !project_eng || project_eng === '') {
    msg = '必須輸入專案及專案資料夾名稱';
    setPopUpMsg(msg);
    setCheckPopUp(true);
  } else {
    msg = 'ok';
  }
  return msg;
}
