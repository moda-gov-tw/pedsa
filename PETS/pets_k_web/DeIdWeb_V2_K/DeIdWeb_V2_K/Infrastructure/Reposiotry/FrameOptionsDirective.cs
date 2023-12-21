namespace DeIdWeb_V2_K.Infrastructure.Reposiotry
{
    public class FrameOptionsDirective : CspDirective
    {
        public FrameOptionsDirective() : base("frame-ancestors")
        {

        }
        public string XFrameOptions { get; private set; }
        public override CspDirective AllowAny()
        {
            XFrameOptions = "";
            return base.AllowAny();
        }
        public override CspDirective Disallow()
        {
            XFrameOptions = "deny";
            return base.Disallow();
        }
        public override CspDirective AllowSelf()
        {
            XFrameOptions = "sameorigin";
            return base.AllowSelf();
        }
        public override CspDirective Allow(string source)
        {
            XFrameOptions = $"allow-from {source}";
            return base.Allow(source);
        }
    }
}
