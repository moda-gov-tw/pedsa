namespace DeIdWeb_V2_K.Infrastructure.Reposiotry
{
    public class CspOptions
    {
        public bool ReadOnly { get; set; }
        public CspDirective Defaults { get; set; } = new CspDirective("default-src");
        public CspDirective Connects { get; set; } = new CspDirective("connect-src");
        public CspDirective Fonts { get; set; } = new CspDirective("font-src");
        public CspDirective Frames { get; set; } = new CspDirective("frame-src");
        public CspDirective Images { get; set; } = new CspDirective("img-src");
        public CspDirective Media { get; set; } = new CspDirective("media-src");
        public CspDirective Objects { get; set; } = new CspDirective("object-src");
        public CspDirective Scripts { get; set; } = new CspDirective("script-src");
        public CspDirective Styles { get; set; } = new CspDirective("style-src");
        public string ReportURL { get; set; }
        public FrameOptionsDirective FrameAncestors { get; set; } = new FrameOptionsDirective();
    }
}
