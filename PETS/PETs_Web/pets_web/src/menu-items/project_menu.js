// third-party
import { FormattedMessage } from 'react-intl';

// ==============================|| MENU ITEMS - PROJECT ||============================== //

const projectMenu = {
  id: '1',
  title: <FormattedMessage id=" " />,
  type: 'group',
  children: [
    {
      id: 'projectList',
      title: <FormattedMessage id="專案列表" />,
      type: 'item',
      url: '/apps/project/projects-table',
      // icon: icons.ManageAccountsOutlinedIcon,
      breadcrumbs: true
    },
    {
      id: 'newProject',
      title: <FormattedMessage id="建立專案及設定" />,
      type: 'not-show',
      url: '/apps/project/new-project',
      // icon: icons.ManageAccountsOutlinedIcon,
      breadcrumbs: false
    },
  ]
};

export default projectMenu;

