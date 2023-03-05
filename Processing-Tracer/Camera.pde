int spp = 1;
 
class Lens {
  public float radius;
  public float dist;
  
  Lens(float radius, float dist) {
    this.radius = radius;
    this.dist = dist;
  }
}
class Camera {
  public Point eye;
  public float d = 1;
  public float fov;
  public float k;
  public int screen_w;
  public int screen_h;
  public int spp;
  public Lens lens;
  
  Camera(float fov, int sw, int sh) {
    this.eye = new Point(0, 0, 0);
    this.fov = fov;
    this.k = tan(radians(fov / 2)) * d;
    this.screen_w = sw;
    this.screen_h = sh;
    this.spp = 1;
  }
  
  public void setFOV(float fov) {
    this.fov = fov;
    this.k = tan(radians(fov / 2)) * d;
  }
  
  public void setSPP(int rayPerPixel) {
    this.spp = rayPerPixel;
  }

  public Ray generateRay(float sx, float sy) {
    Point viewCoord = null;
    Ray ray = null;
     
    if (lens != null) {
      viewCoord = calcViewPlaneCoord(sx, sy);
      Point newEye = sample();
      PVector dir = new PVector(viewCoord.x - eye.x, 
                                viewCoord.y - eye.y,
                                viewCoord.z - eye.z);
      dir.normalize();                       
      float fx = eye.x + lens.dist * dir.x;
      float fy = eye.y + lens.dist * dir.y;
      float fz = eye.z + lens.dist * dir.z;
      Point fp = new Point(fx, fy, fz);
      ray = new Ray(newEye, fp, false, -1);
    } else {
      viewCoord = calcViewPlaneCoord(sx, sy);
      ray = new Ray(eye, viewCoord, false, -1);
    }
    
    return ray;
  }
  
  private Point sample() {
    while (true) {
      float x = random(-lens.radius, lens.radius);
      float y = random(-lens.radius, lens.radius);
      
      float distSqure = x * x + y * y;
      //println("distSqure: " + distSqure + "r^2: " + radius * radius);
      if (distSqure <= lens.radius * lens.radius) {
        float dx = eye.x + x;
        float dy = eye.y + y;
        return new Point(dx, dy, 0);
      }
    }
  }
  
  public void useLens(Lens lens) {
    this.lens = lens;
  }

  private Point calcViewPlaneCoord(float sx, float sy) {
    float vx = (sx - this.screen_w/2) * (2 * (this.k) / this.screen_w);
    float vy = (sy - this.screen_h/2) * (2 * (this.k) / this.screen_h);
    return new Point(vx, vy, -1);
  }
  
}
