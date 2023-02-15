class BBox extends SceneObject implements HitTest {
  public float[] min3;
  public float[] max3;
  Color diffuse;
  PVector normal;
  Point center;
  float[] dunit;
  boolean needNormal;
  
  BBox(Color c, float[] min3, float[] max3, boolean needNormal) {
    diffuse = c;
    this.min3 = min3;
    this.max3 = max3;
    float cx = (min3[0] + max3[0])/2;
    float cy = (min3[1] + max3[1])/2;
    float cz = (min3[2] + max3[2])/2;
    this.center = new Point(cx, cy, cz);
    
    float unitx = Math.abs(min3[0] - max3[0])/2;
    float unity = Math.abs(min3[1] - max3[1])/2;
    float unitz = Math.abs(min3[2] - max3[2])/2;
    this.dunit = new float[]{unitx, unity, unitz};
    this.needNormal = needNormal;
  }
 
  
  public Hit isHit(Ray ray) {
    //if (debug_flag && ray.shadowRay) {
    //  println("debug ray!");
    //}
    float[] dir3 = ray.dir.array();
    float min = -Float.MAX_VALUE;
    float max = Float.MAX_VALUE;
    
    for (int i = 0; i < 3; i++) {
      float tMin = (min3[i] - ray.origin.p3[i]) / dir3[i];
      float tMax = (max3[i] - ray.origin.p3[i]) / dir3[i];
     
      if (tMin > tMax) {
        float tmp = tMin;
        tMin = tMax;
        tMax = tmp;
      }
      min = Math.max(min, tMin);
      max = Math.min(max, tMax);
    }
    if (min > max) {
      return null;
    }
    
    t = min;
    Point p = getHitPoint(ray, t);
    
    if (needNormal) {
      float bias = 1.000001;
      PVector pc = new PVector(p.x - center.x, p.y - center.y, p.z - center.z);
      int x = int((pc.x * bias)/dunit[0]);
      int y = int((pc.y * bias)/dunit[1]);
      int z = int((pc.z * bias)/dunit[2]);
      
      //div by 0, hack for failed rotation in scene2
      if (dunit[1] == 0) { 
        y = 1;
      }
      normal = new PVector(x, y, z);
    }
    
    return new Hit(diffuse, p, normal, ray, t);
  }
}
