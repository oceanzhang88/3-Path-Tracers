interface HitTest {
  Hit isHit(Ray ray);
}

class Hit {
  public Color diffuse;
  public Material material;
  public Point p;
  public PVector normal;
  public Ray ray;
  public float t;
  public int objectId = -1;
  
  Hit(Color c, Point p, PVector normal, Ray ray, float t) {
    this.diffuse = c;
    this.p = p;
    this.normal = normal;
    this.ray = ray;
    this.t = t;
  }
  
  Hit(Material material, Point p, PVector normal, Ray ray, float t) {
    this.material = material;
    this.p = p;
    this.normal = normal;
    this.ray = ray;
    this.t = t;
  }
}
