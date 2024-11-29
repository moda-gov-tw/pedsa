// third-party
import ListAltOutlinedIcon from '@mui/icons-material/ListAltOutlined';
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
      breadcrumbs: true,
      icon: ListAltOutlinedIcon
    },
    {
      id: 'newProject',
      title: <FormattedMessage id="建立專案及設定" />,
      type: 'not-show',
      url: '/apps/project/new-project',
      breadcrumbs: false,
      icon: ListAltOutlinedIcon
    }
  ]
};

export default projectMenu;
