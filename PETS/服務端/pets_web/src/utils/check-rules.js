export function checkEmail(s) {
    //if (typeof (s) === 'string') {
    // console.log('s', s);
    //  if (!s.includes('@')) {
    //      return false;
    //  }
    // }
    // return true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (typeof s === 'string') {
        return emailRegex.test(s);
    }
    return false;
}

export function checkEmailMsg(s) {
    if (!s) {
        return '信箱為必填';
    }
    if (typeof (s) === 'string') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(s)) {
            return '請輸入正確信箱格式';
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

export function containsTabOrSpace(str) {
    const tabAndSpace = /[\t ]/;
    return tabAndSpace.test(str);
}

export function containsChineseChars(str) {
    // 不可以包含中文字元
    const regExp = /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]/g;
    return regExp.test(str);
}

export function containsNotOnlyNumbers(str) {
    const tmp = Number(str);
    if (!isNaN(tmp)) {
        return false;
    }
    return true;
}

export function containsFullWidthChars(str) {
    const fullWidthChars = /[\uFF00-\uFFEF\u3000]/;
    return fullWidthChars.test(str);
}

export function checkUseraccount(str) {
    if (containsSpecialChars2(str) || containsChineseChars(str) || containsTabOrSpace(str) || containsFullWidthChars(str)) {
        return true;
    }
    return false;
}

export function checkUsername(str) {
    if (containsSpecialChars1(str)) {
        return true;
    }
    return false;
}

export function checkProject(str) {
    if (containsSpecialChars2(str) || containsTabOrSpace(str) || containsFullWidthChars(str)) {
        return true;
    }
    return false;
}

export function checkfilecsv(str) {
    // 检查文件名是否以 .csv 结尾
    if (value.endsWith('.csv')) {
        return true;
    }

    return false;
}

//增加確認全數字與第一個字不能為數字邏輯判斷
export function checkProjectFolder(str) {
    if (containsSpecialChars2(str) || containsChineseChars(str) || containsTabOrSpace(str) || containsFullWidthChars(str)) {
        return true;
    }
    const allNumbersRegex = /^\d+$/;
    if (allNumbersRegex.test(str)) {
        return true;
    }
    const startsWithNumberRegex = /^\d/;
    if (startsWithNumberRegex.test(str)) {
        return true;
    }
    return false;
}

export function checkGroupName(str) {
    if (containsSpecialChars2(str)) {
        return true;
    }
    return false;
}

export function checkGroupType(str) {
    if (containsSpecialChars1(str) || containsChineseChars(str) || str.length > 5) {
        return true;
    }
    return false;
}

export function checkGroupQuota(str) {
    if (containsNotOnlyNumbers(str)) {
        return true;
    }
    return false;
}