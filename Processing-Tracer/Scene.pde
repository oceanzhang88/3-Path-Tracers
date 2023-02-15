class SceneObject {
  protected float t;
  
  protected Point getHitPoint(Ray ray, float t) {
    float x = ray.origin.x + t * ray.dir.x;
    float y = ray.origin.y + t * ray.dir.y;
    float z = ray.origin.z + t * ray.dir.z;
    return new Point(x, y, z);
  }
}

class Camera {
  Point eye;
  float d = 1;
  float fov;
  float k;
  int screen_w;
  int screen_h;
  Camera(float fov, int sw, int sh) {
    this.eye = new Point(0, 0, 0);
    this.fov = fov;
    this.k = tan(radians(fov / 2)) * d;
    this.screen_w = sw;
    this.screen_h = sh;
  }

  public Ray generateRay(int sx, int sy) {
    Point viewCoord = calcViewPlaneCoord(sx, sy);
    Ray ray = new Ray(eye, viewCoord, false, -1);
    //println("Gen Ray: '" + ray.dir + "'");
    return ray;
  }

  private Point calcViewPlaneCoord(int sx, int sy) {
    float vx = (sx - this.screen_w/2) * (2 * this.k / this.screen_w);
    float vy = (sy - this.screen_h/2) * (2 * this.k / this.screen_h);
    return new Point(vx, vy, -1);
  }
}

class Scene {
  public Color bkColor;
  public Camera camera;
  public ArrayList<Light> lights;
  public ArrayList<SceneObject> objects;
  public int screen_w;
  public int screen_h;

  Scene() {
    objects = new ArrayList<SceneObject>();
    lights = new ArrayList<Light>();
  }

  public void addLight(Light light) {
    lights.add(light);
  }
  
  public SceneObject getLastObject() {
    int index = objects.size() - 1;
    return objects.get(index);
  }
  
  public SceneObject removeLastObject() {
    int index = objects.size() - 1;
    return objects.remove(index);
  }
  
  public Hit castRay(Ray ray) {
    float min_dist = Float.MAX_VALUE;
    Hit nearestHit = null;
    for (int i = 0; i < objects.size(); i++) {
      if (ray.shadowRay && ray.objectId == i) 
          continue;
          
      SceneObject so = objects.get(i);
      HitTest tester = getHitTest(so);
      Hit hit = tester.isHit(ray);
      
      if (hit == null) {
        continue;
      }
      if (ray.shadowRay) {
        if (hit.t > 0 && hit.t < 1)
          return hit;
        if (hit.t > 1) 
          continue;
      }
      
      if (hit.t > 0 && hit.t < min_dist) {
        min_dist = min(min_dist, hit.t);
        nearestHit = hit;
        hit.objectId = i;
      }
    }
    //if (debug_flag) {
    //  println("triangle inst", ray.shadowRay);
    //}
    return nearestHit;
  }
  
  public boolean isOcculuded(Hit hit, Light light) {
    Point p = hit.p;
    Point pLight = new Point(light.x, light.y, light.z);
    Ray shadowRay = new Ray(p, pLight, true, light.id);
    shadowRay.objectId = hit.objectId;
    //shadowRay.dir.normalize();
    Hit inshadow = castRay(shadowRay);
    return inshadow != null;
  }
}
