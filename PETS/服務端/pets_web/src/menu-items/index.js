// project import
import functions from "./function_menu";
import projectMenu from "./project_menu";
import groupMenu from "./group_menu";
import userMenu from "./user_menu";
import sysMenu from "./system_menu";
import historyProjectMenu from "./history_project_menu";
import personalSettingMenu from "./personal_setting_menu";

// ==============================|| MENU ITEMS ||============================== //
const menuItems = {

  // items: [widget, applications, formsTables, chartsMap, pages, mdms, other]
  items: [projectMenu, groupMenu, userMenu, sysMenu, historyProjectMenu, personalSettingMenu]
};

export default menuItems;
