// third-party
import { FormattedMessage } from 'react-intl';

// ==============================|| MENU ITEMS - HISTORY PROJECT ||============================== //

const historyProjectMenu = {
  id: '5',
  title: <FormattedMessage id=" " />,
  type: 'group',
  children: [
    {
      id: 'historyProjectList',
      title: <FormattedMessage id="歷史專案列表" />,
      type: 'item',
      url: '/apps/project/history-projects-table',
      // icon: icons.ManageAccountsOutlinedIcon,
      breadcrumbs: true
    },
  ]
};

export default historyProjectMenu;

