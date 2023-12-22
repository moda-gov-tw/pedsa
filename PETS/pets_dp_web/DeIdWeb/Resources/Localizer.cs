namespace Resources
{
  using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;
    using System.Reflection;
    using System.Resources;
    using System.Runtime.Loader;
    using System.Text.RegularExpressions;

    public interface ILocalizer
    {
    string Culture { get; set; }

    Message Message { get; }

    Text Text { get; }

        string GetString(Type category, string resourceKey);

        string GetString(string category, string resourceKey);

        string GetString(Type category, string resourceKey, string culture);

        string GetString(string category, string resourceKey, string culture);
    }

    public class Localizer : ILocalizer
    {
        private const string DefaultCulture = "zh-TW";
        private static readonly Lazy<Dictionary<string, ResourceManager>> _resources = new Lazy<Dictionary<string, ResourceManager>>(LoadResourceManager);
    private static string _assemblyPath;
        private string _culture;
        private Message _message;
        private Text _text;

    public Localizer() {
      _assemblyPath = Assembly.GetEntryAssembly().Location;
    }

    public Localizer(string assemblyPath) {
      _assemblyPath = assemblyPath;
    }
            
        #region ILocalizer

    public string Culture
        {
            get
            {
                if (string.IsNullOrEmpty(_culture))
                {
                    _culture = DefaultCulture;
                }
                return _culture;
            }
            set
            {
                var culture = value;
                if (Regex.IsMatch(culture, @"^[A-Za-z]{2}-[A-Za-z]{2}$"))
                {
                    _culture = culture;
                }
                else
                {
                    _culture = DefaultCulture;
                }
            }
        }

    public Message Message { get { if (_message == null) { _message = new Message(this); } return _message; } }

    public Text Text { get { if (_text == null) { _text = new Text(this); } return _text; } }

        public string GetString(Type category, string resourceKey)
        {
            return GetString(category.Name.ToString(), resourceKey);
        }

        public string GetString(string category, string resourceKey)
        {
            return GetString(category, resourceKey, _culture);
        }

        public string GetString(Type category, string resourceKey, string culture)
        {
            return GetString(category.Name.ToString(), resourceKey, culture);
        }

        public string GetString(string category, string resourceKey, string culture)
        {
            var resource = GetResource($"{category}.{culture}") ?? GetResource($"{category}.{DefaultCulture}");
            if (resource == null)
            {
                return resourceKey;
            }
            else
            {
                return resource.GetString(resourceKey);
            }
        }

        #endregion ILocalizer

        #region Private Methods

        private static Dictionary<string, ResourceManager> LoadResourceManager()
        {
            var directory = Path.GetDirectoryName(_assemblyPath);
            var files = Directory.GetFiles(directory, "*.resources.dll", SearchOption.AllDirectories);
            
            var resources = new Dictionary<string, ResourceManager>(StringComparer.CurrentCultureIgnoreCase);
            foreach (var file in files)
            {
                var culture = Path.GetFileName(Path.GetDirectoryName(file));
                var assembly = AssemblyLoadContext.Default.LoadFromAssemblyPath(file);
                foreach (var resourceName in assembly.GetManifestResourceNames().Select(s => Regex.Replace(s, ".resources$", "")))
                {
                    var category = Regex.Match(resourceName, $".*Resources\\.(.*)\\.{culture}").Groups[1].Value;
                    //var resourceManager = new ResourceManager(resourceName, assembly);
                    //if (category != "")
                    //    resources.Add($"{category}.{culture}", resourceManager);
                    // 檢查字典中是否已經包含相同的鍵
                    var key = $"{category}.{culture}";
                    if (!resources.ContainsKey(key))
                    {
                        var resourceManager = new ResourceManager(resourceName, assembly);
                        if (category != "")
                            resources.Add(key, resourceManager);
                    }
                }
            }

            return resources;
        }

        private ResourceManager GetResource(string key)
        {
            if (_resources.Value.Keys.Contains(key))
            {
                return _resources.Value[key];
            }
            return null;
        }

        #endregion
    }

    public abstract class ResourceBase
    {
        protected ResourceBase(ILocalizer localizer)
        {
            Localizer = localizer;
        }

        protected ILocalizer Localizer { get; private set; }

        protected string GetString(string resourceKey)
        {
            return Localizer.GetString(GetType(), resourceKey);
        }
    }

    public class Message : ResourceBase
    {
        public Message(ILocalizer localizer) : base(localizer)
        {
        }

    public string Check_reset { get { return GetString("Check_reset"); } }

    public string Dataset_empty { get { return GetString("Dataset_empty"); } }

    public string deid_error { get { return GetString("deid_error"); } }

    public string deleted { get { return GetString("deleted"); } }

    public string delete_project_confirm { get { return GetString("delete_project_confirm"); } }

    public string del_error { get { return GetString("del_error"); } }

    public string do_deid { get { return GetString("do_deid"); } }

    public string export { get { return GetString("export"); } }

    public string export_error { get { return GetString("export_error"); } }

    public string gen_error { get { return GetString("gen_error"); } }

    public string gen_job { get { return GetString("gen_job"); } }

    public string gen_processing { get { return GetString("gen_processing"); } }

    public string import { get { return GetString("import"); } }

    public string import_not_finish { get { return GetString("import_not_finish"); } }

    public string jobing { get { return GetString("jobing"); } }

    public string job_run_error { get { return GetString("job_run_error"); } }

    public string job_save { get { return GetString("job_save"); } }

    public string job_save_error { get { return GetString("job_save_error"); } }

    public string login_failed { get { return GetString("login_failed"); } }

    public string no_account { get { return GetString("no_account"); } }

    public string no_k_value { get { return GetString("no_k_value"); } }

    public string passwd_error { get { return GetString("passwd_error"); } }

    public string pname_duplicate { get { return GetString("pname_duplicate"); } }

    public string project_check { get { return GetString("project_check"); } }

    public string project_create_engcheck { get { return GetString("project_create_engcheck"); } }

    public string project_desc { get { return GetString("project_desc"); } }

    public string project_exportpath { get { return GetString("project_exportpath"); } }

    public string project_insert_error { get { return GetString("project_insert_error"); } }

    public string project_owner { get { return GetString("project_owner"); } }

    public string project_path { get { return GetString("project_path"); } }

    public string project_status_error { get { return GetString("project_status_error"); } }

    public string reset_error { get { return GetString("reset_error"); } }

    public string reset_finish { get { return GetString("reset_finish"); } }

    public string save_col_error { get { return GetString("save_col_error"); } }

    public string job_run { get { return GetString("job_run"); } }

    public string select_dataset { get { return GetString("select_dataset"); } }

    public string k_num_check { get { return GetString("k_num_check"); } }

    public string updown_error { get { return GetString("updown_error"); } }

    public string updown_num_error { get { return GetString("updown_num_error"); } }

    public string updown_up_error { get { return GetString("updown_up_error"); } }
    }

    public class Text : ResourceBase
    {
        public Text(ILocalizer localizer) : base(localizer)
        {
        }

    public string About { get { return GetString("About"); } }

    public string add { get { return GetString("add"); } }

    public string add_member { get { return GetString("add_member"); } }

    public string back { get { return GetString("back"); } }

    public string check_ed { get { return GetString("check_ed"); } }

    public string ch_col_name { get { return GetString("ch_col_name"); } }

    public string col_attr { get { return GetString("col_attr"); } }

    public string col_name { get { return GetString("col_name"); } }

    public string customize { get { return GetString("customize"); } }

    public string customize_info { get { return GetString("customize_info"); } }

    public string dataset_name { get { return GetString("dataset_name"); } }

    public string data_attr { get { return GetString("data_attr"); } }

    public string data_g { get { return GetString("data_g"); } }

    public string date { get { return GetString("date"); } }

    public string deid_ing { get { return GetString("deid_ing"); } }

    public string deid_risk { get { return GetString("deid_risk"); } }

    public string delete { get { return GetString("delete"); } }

    public string do_k { get { return GetString("do_k"); } }

    public string en_col_name { get { return GetString("en_col_name"); } }

    public string export { get { return GetString("export"); } }

    public string finish { get { return GetString("finish"); } }

    public string format { get { return GetString("format"); } }

    public string g_and_sensitive { get { return GetString("g_and_sensitive"); } }

    public string g_setting { get { return GetString("g_setting"); } }

    public string home { get { return GetString("home"); } }

    public string import { get { return GetString("import"); } }

    public string job_info { get { return GetString("job_info"); } }

    public string join { get { return GetString("join"); } }

    public string join_method { get { return GetString("join_method"); } }

    public string key_words { get { return GetString("key_words"); } }

    public string k_anonymity { get { return GetString("k_anonymity"); } }

    public string k_delete { get { return GetString("k_delete"); } }

    public string k_sup { get { return GetString("k_sup"); } }

    public string k_value { get { return GetString("k_value"); } }

    public string maximum { get { return GetString("maximum"); } }

    public string max_sup_r { get { return GetString("max_sup_r"); } }

    public string method { get { return GetString("method"); } }

    public string method_setting { get { return GetString("method_setting"); } }

    public string minimum { get { return GetString("minimum"); } }

    public string muti_key { get { return GetString("muti_key"); } }

    public string next { get { return GetString("next"); } }

    public string nonproject { get { return GetString("nonproject"); } }

    public string notification { get { return GetString("notification"); } }

    public string no_data { get { return GetString("no_data"); } }

    public string no_k { get { return GetString("no_k"); } }

    public string no_process { get { return GetString("no_process"); } }

    public string numerical_interval { get { return GetString("numerical_interval"); } }

    public string numerical_interval_gr { get { return GetString("numerical_interval_gr"); } }

    public string numerical_interval_group_name { get { return GetString("numerical_interval_group_name"); } }

    public string num_min { get { return GetString("num_min"); } }

    public string num_max { get { return GetString("num_max"); } }

    public string num_updown { get { return GetString("num_updown"); } }

    public string outlier_upper_bound { get { return GetString("outlier_upper_bound"); } }

    public string primary_data { get { return GetString("primary_data"); } }

    public string project_list { get { return GetString("project_list"); } }

    public string report_management { get { return GetString("report_management"); } }

    public string run { get { return GetString("run"); } }

    public string save { get { return GetString("save"); } }

    public string select { get { return GetString("select"); } }

    public string select_dataset { get { return GetString("select_dataset"); } }

    public string select_method { get { return GetString("select_method"); } }

    public string setting_ed { get { return GetString("setting_ed"); } }

    public string single { get { return GetString("single"); } }

    public string single_key { get { return GetString("single_key"); } }

    public string step2_info { get { return GetString("step2_info"); } }

    public string substring { get { return GetString("substring"); } }

    public string sup { get { return GetString("sup"); } }

    public string total_records { get { return GetString("total_records"); } }

    public string unit_interval { get { return GetString("unit_interval"); } }

    public string upload_ed { get { return GetString("upload_ed"); } }

    public string utility { get { return GetString("utility"); } }

    public string vice_data { get { return GetString("vice_data"); } }

    public string dir_id { get { return GetString("dir_id"); } }

    public string gen_preview { get { return GetString("gen_preview"); } }

    public string others { get { return GetString("others"); } }

    public string qi_id { get { return GetString("qi_id"); } }

    public string sensitive_id { get { return GetString("sensitive_id"); } }

    public string step1 { get { return GetString("step1"); } }

    public string step1_info { get { return GetString("step1_info"); } }

    public string step2 { get { return GetString("step2"); } }

    public string step3 { get { return GetString("step3"); } }

    public string step4 { get { return GetString("step4"); } }

    public string step5 { get { return GetString("step5"); } }

    public string unuse { get { return GetString("unuse"); } }

    public string add_project { get { return GetString("add_project"); } }

    public string confirm { get { return GetString("confirm"); } }

    public string cust_key { get { return GetString("cust_key"); } }

    public string data_path { get { return GetString("data_path"); } }

    public string data_suprate { get { return GetString("data_suprate"); } }

    public string desc { get { return GetString("desc"); } }

    public string distinct { get { return GetString("distinct"); } }

    public string export_path { get { return GetString("export_path"); } }

    public string gen_setting { get { return GetString("gen_setting"); } }

    public string min_kvalue { get { return GetString("min_kvalue"); } }

    public string new_project { get { return GetString("new_project"); } }

    public string no_col { get { return GetString("no_col"); } }

    public string process_flow { get { return GetString("process_flow"); } }

    public string project_leader { get { return GetString("project_leader"); } }

    public string project_name { get { return GetString("project_name"); } }

    public string project_dataset_name { get { return GetString("project_dataset_name"); } }

    public string raw_data { get { return GetString("raw_data"); } }

    public string k_checking_data { get { return GetString("k_checking_data"); } }

    public string count { get { return GetString("count"); } }

    public string dis_count { get { return GetString("dis_count"); } }

    public string raw_data_count { get { return GetString("raw_data_count"); } }

    public string un_keycount { get { return GetString("un_keycount"); } }

    public string result_deid { get { return GetString("result_deid"); } }

    public string tb { get { return GetString("tb"); } }

    public string union { get { return GetString("union"); } }

    public string account { get { return GetString("account"); } }

    public string account_man { get { return GetString("account_man"); } }

    public string dataset_attr { get { return GetString("dataset_attr"); } }

    public string dataset_attr_check { get { return GetString("dataset_attr_check"); } }

    public string data_gen_setting { get { return GetString("data_gen_setting"); } }

    public string data_importing { get { return GetString("data_importing"); } }

    public string data_info { get { return GetString("data_info"); } }

    public string data_processing { get { return GetString("data_processing"); } }

    public string data_processing_no { get { return GetString("data_processing_no"); } }

    public string deid_finish { get { return GetString("deid_finish"); } }

    public string deid_process { get { return GetString("deid_process"); } }

    public string del_project { get { return GetString("del_project"); } }

    public string index_feature_01 { get { return GetString("index_feature_01"); } }

    public string index_feature_02 { get { return GetString("index_feature_02"); } }

    public string index_feature_03 { get { return GetString("index_feature_03"); } }

    public string index_feature_04 { get { return GetString("index_feature_04"); } }

    public string login { get { return GetString("login"); } }

    public string logout { get { return GetString("logout"); } }

    public string management { get { return GetString("management"); } }

    public string passwd { get { return GetString("passwd"); } }

    public string profile { get { return GetString("profile"); } }

    public string project_man { get { return GetString("project_man"); } }

    public string project_text { get { return GetString("project_text"); } }

    public string reset_project { get { return GetString("reset_project"); } }

    public string title { get { return GetString("title"); } }

    public string web_contentlist { get { return GetString("web_contentlist"); } }

    public string jobname { get { return GetString("jobname"); } }

    public string step4_distinct { get { return GetString("step4_distinct"); } }

    public string step4_join { get { return GetString("step4_join"); } }

    public string step4_single { get { return GetString("step4_single"); } }

    public string step4_union { get { return GetString("step4_union"); } }

    public string step1_menu_list { get { return GetString("step1_menu_list"); } }

    public string step2_menu_list { get { return GetString("step2_menu_list"); } }

    public string step3_menu_list { get { return GetString("step3_menu_list"); } }

    public string step4_menu_list { get { return GetString("step4_menu_list"); } }

    public string step5_menu_list { get { return GetString("step5_menu_list"); } }

    public string step6_menu_list { get { return GetString("step6_menu_list"); } }

    public string chose_config { get { return GetString("chose_config"); } }

    public string col_check { get { return GetString("col_check"); } }

    public string col_map_success { get { return GetString("col_map_success"); } }

    public string col_map_fail { get { return GetString("col_map_fail"); } }

    public string config_error { get { return GetString("config_error"); } }

    public string json_txt_check { get { return GetString("json_txt_check"); } }

    public string load_config { get { return GetString("load_config"); } }

    public string load_data { get { return GetString("load_data"); } }

    public string load_finish { get { return GetString("load_finish"); } }

    public string load_error { get { return GetString("load_error"); } }

    public string map_error { get { return GetString("map_error"); } }

    public string no_select_file { get { return GetString("no_select_file"); } }

    public string select_file { get { return GetString("select_file"); } }

    public string data_count { get { return GetString("data_count"); } }

    public string report_info1 { get { return GetString("report_info1"); } }

    public string report_info2 { get { return GetString("report_info2"); } }

    public string warning_info { get { return GetString("warning_info"); } }

    public string checkyes_msg { get { return GetString("checkyes_msg"); } }

    public string dept_title { get { return GetString("dept_title"); } }

    public string rp_id_col { get { return GetString("rp_id_col"); } }

    public string Index_Error { get { return GetString("Index_Error"); } }

    public string Index_GanReport { get { return GetString("Index_GanReport"); } }

    public string Index_Gan_Processing { get { return GetString("Index_Gan_Processing"); } }

    public string Index_Gan_Setting { get { return GetString("Index_Gan_Setting"); } }

    public string Index_ML_Processing { get { return GetString("Index_ML_Processing"); } }

    public string Index_ML_Setting { get { return GetString("Index_ML_Setting"); } }

    public string Index_Gan_Error { get { return GetString("Index_Gan_Error"); } }

    public string Index_ML_Error { get { return GetString("Index_ML_Error"); } }

    public string Index_Project_Create { get { return GetString("Index_Project_Create"); } }

    public string Index_Gan_Export_Processing { get { return GetString("Index_Gan_Export_Processing"); } }
    }
}
