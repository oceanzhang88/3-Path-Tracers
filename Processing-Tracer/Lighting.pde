interface Light {
  Point center();
  int id();
  Color lcolor();
}

class DirectionalLight implements Light {
  float x;
  float y;
  float z;
  
  Color lcolor;
  int id;

  DirectionalLight(float x, float y, float z, Color c, int id) {
    this.x = x;
    this.y = y;
    this.z = z;

    lcolor = c;
    this.id = id;
  }
  
  public Point center() {
    return new Point(x, y, z);
  }
  
  public int id() {
    return id;
  }
  
  public Color lcolor() {
    return lcolor;
  }
}

class SpotLight implements Light {
  public Point center;
  public PVector normal;
  public float radius;
  public Color rgb;
  public int id;

  SpotLight(Point center, PVector normal, float radius, Color rgb, int id) {
    this.center = center;
    this.normal = normal;
    this.normal.normalize();
    this.rgb = rgb;
    this.id = id;
    this.radius = radius;
  }
  
  public Point center() {
    return center;
  }
  
  public Color lcolor() {
    return rgb;
  }
  
  public Point sample() {
    while (true) {
      float rx = random(-radius, radius);
      float rz = random(-radius, radius);
      float distSqure = rx * rx + rz * rz;
      
      if (distSqure <= radius * radius) {
        float ry = -(normal.x * rx + normal.z * rz) / normal.y;
        float dx = center.x + rx;
        float dz = center.z + rz;
        float dy = center.y + ry;
        return new Point(dx, dy, dz);
      }
    }
  }
  
  public int id() {
    return id;
  }
}
