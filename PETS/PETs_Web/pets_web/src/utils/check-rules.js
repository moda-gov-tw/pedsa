export function checkEmail(s) {
    if(typeof(s) === 'string') {
        // console.log('s', s);
        if(!s.includes('@')) {
            return false;
        }
    }
    return true;
}

export function checkEmailMsg(s) {
    if(!s){
        return '信箱為必填';
    }
    if(typeof(s) === 'string') {
        if(!s.includes('@')) {
            return '請輸入可用的信箱';
        }
    }
}

export function containsSpecialChars1(str) {
  // 不可包含任何特殊符號包含下底線
  const specialChars = /[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;
  return specialChars.test(str);
}

export function containsSpecialChars2(str) {
  // 不可包含特殊符號，但是可以包含下底線
  const specialChars = /[`!@#$%^&*()+\-=\[\]{};':"\\|,.<>\/?~]/;
  return specialChars.test(str);
}

export function containsChineseChars(str) {
    // 不可以包含中文字元
    const regExp = /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]/g;
    return regExp.test(str);
}

export function containsNotOnlyNumbers(str) {
    const tmp = Number(str);
    if(!isNaN(tmp)) {
        return false;
    }
    return true;
}

export function checkUseraccount(str) {
    if(containsSpecialChars2(str) || containsChineseChars(str)) {
        return true;
    }
    return false;
}

export function checkUsername(str) {
    if(containsSpecialChars1(str)) {
        return true;
    }
    return false;
}

export function checkProject(str) {
    if(containsSpecialChars2(str)) {
        return true;
    }
    return false;
}

export function checkProjecFolder(str) {
    if(containsSpecialChars2(str) || containsChineseChars(str)) {
        return true;
    }
    return false;
}

export function checkGroupName(str) {
    if(containsSpecialChars2(str)) {
        return true;
    }
    return false;
}

export function checkGroupType(str) {
    if(containsSpecialChars1(str) || containsChineseChars(str) || str.length>3) {
        return true;
    }
    return false;
}

export function checkGroupQuota(str) {
    if(containsNotOnlyNumbers(str)) {
        return true;
    }
    return false;
}