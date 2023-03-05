abstract class SceneObject {
  protected float t;
  protected boolean motionBlur;
  protected float dx;
  protected float dy;
  protected float dz;
  protected Material material;
  protected int id;
  
  SceneObject() {
    this.dx = -1;
    this.dy = -1;
    this.dz = -1;
    this.motionBlur = false;
  }
  
  protected Point getHitPoint(Ray ray, float t) {
    float x = ray.origin.x + t * ray.dir.x;
    float y = ray.origin.y + t * ray.dir.y;
    float z = ray.origin.z + t * ray.dir.z;
  
    return new Point(x, y, z);
  }
  
  protected void useMotionBlur(float dx, float dy, float dz) {
    this.motionBlur = true;
    this.dx = dx;
    this.dy = dy;
    this.dz = dz;
  }
  
  protected abstract Point center();
  
  public void setMaterial(Material material) {
    this.material = material;
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
      if (ray.shadowRay && ray.objectId == i) {
        continue;
      }

      SceneObject so = objects.get(i);
      HitTest tester = getHitTest(so);
      Hit hit = null;
      if (!so.motionBlur) {
        hit = tester.isHit(ray);
      } else {
        float t = random(0, 1);

        Ray newRay = new Ray(ray.shadowRay);
        float px = ray.origin.x - t * so.dx;
        float py = ray.origin.y - t * so.dy;
        float pz = ray.origin.z - t * so.dz;
        Point newOrigin = new Point(px, py, pz);
        newRay.origin = newOrigin;
        newRay.objectId = ray.objectId;
        newRay.target = ray.target;
        newRay.dir = ray.dir;
    
        hit = tester.isHit(newRay);  
      }
      
      if (hit == null) {
        continue;
      }
      if (ray.shadowRay) {
        if (hit.t > 0 && hit.t < 1) {
          return hit;
        } else {
          continue;
        }
      }
      
      if (hit.t > 0 && hit.t < min_dist) {
        min_dist = min(min_dist, hit.t);
        nearestHit = hit;
        hit.objectId = i;
      }
    }
    return nearestHit;
  }
  
  public boolean isOcculuded(Hit hit, Point lcenter) {
    Point p = hit.p;                         
    Ray shadowRay = new Ray(p, lcenter, true, hit.objectId);
    Hit inshadow = castRay(shadowRay);
    return inshadow != null;
  }
}
