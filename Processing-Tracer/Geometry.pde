class Point {
  public float x;
  public float y;
  public float z;
  public float w;
  
  public float[] p3;

  Point(float x, float y, float z) {
    this.x = x;
    this.y = y;
    this.z = z;
    this.w = 1;
    this.p3 = new float[]{x, y, z};
  }

  @Override
    public String toString() {
    return "x: " + this.x + "y: " + this.y + "z: " + this.z + "w: " + this.w + "\n";
  }
}

class Ray {
  public PVector dir;
  public Point origin;
  public boolean shadowRay;
  public int objectId = -1;
  public Point target;

  Ray (boolean shadowRay) {
    this.shadowRay = shadowRay;
  }
  
  
  Ray(Point eye, Point target, boolean shadowRay, int objectId) {
    this(shadowRay);
    float x = target.x - eye.x;
    float y = target.y - eye.y;
    float z = target.z - eye.z;
    dir = new PVector(x, y, z);
    origin = eye;
    this.objectId = objectId;
    this.target = target;
  }
  
  Ray(Point eye, PVector dir, boolean shadowRay, int objectId) {
    this(shadowRay);
    this.dir = dir;
    origin = eye;
    this.objectId = objectId;
  }
  
  
  public void calibrateDir() {
    float x = target.x - origin.x;
    float y = target.y - origin.y;
    float z = target.z - origin.z;
    dir = new PVector(x, y, z);
  }
}

class Triangle extends SceneObject implements HitTest {
  public Point[] abc;
  int count = 0;
  Point centriod;
  
  PVector normal;
  float a, b, c, d;
  
  Triangle(Material mat) {
    this.abc = new Point[3];
    this.material = mat; 
  }
  
  public Point center(){
    return null;
  }

  public BBox getBBox() {
    float[] min3 = getMin3();
    float[] max3 = getMax3();
    
    return new BBox(blackMat, min3, max3, false);
  }
  
  public float[] getMin3() {
    float minx = Float.MAX_VALUE;
    float miny = Float.MAX_VALUE;
    float minz = Float.MAX_VALUE;
    for (int i = 0; i < 3; i++) {
      float x = abc[i].x;
      float y = abc[i].y;
      float z = abc[i].z;
      minx = Math.min(minx, x);
      miny = Math.min(miny, y);
      minz = Math.min(minz, z);
     
    }
    float[] min3 = new float[] {minx, miny, minz};
    return min3;
  }
  
  public float[] getMax3() {
   
    float maxx = -Float.MAX_VALUE;
    float maxy = -Float.MAX_VALUE;
    float maxz = -Float.MAX_VALUE;
    for (int i = 0; i < 3; i++) {
      float x = abc[i].x;
      float y = abc[i].y;
      float z = abc[i].z;
     
      maxx = Math.max(maxx, x);
      maxy = Math.max(maxy, y);
      maxz = Math.max(maxz, z);
    }
    float[] max3 = new float[] {maxx, maxy, maxz};
    return max3;
  }
  
  private void genTriPlane() {
    //Use scene winding order instead of flipping normal
    if (WO == WindingOrder.CW) {
      normal = getVecAB().cross(getVecAC());
    } else {
      normal = getVecAC().cross(getVecAB());
    }
    normal.normalize();
    if (normal.y == -1.0) {
      normal.y = 1.0;
    }
    
    if (debug_flag) {
       println("side 1, 2, 3: ");
    }

    this.a = normal.x;
    this.b = normal.y;
    this.c = normal.z;
    Point verta = getVertA();
    this.d = -(a * verta.x + b * verta.y + c * verta.z);
  }
  
  public Color getColor() {
    return material.diffuseColor;
  }

  public void setVertex(Point v) {
    abc[count] = v;
    count++;
    if(count == 3) {
      genTriPlane();
    }
  }
  
  public Point centroid() {
    if(centriod == null) {
      float x = (abc[0].x + abc[1].x + abc[2].x) / 3;
      float y = (abc[0].y + abc[1].y + abc[2].y) / 3;
      float z = (abc[0].z + abc[1].z + abc[2].z) / 3;
      centriod = new Point(x, y, z);
    }
    return centriod;
  }
 
  public PVector getVecAB() {
    float x = abc[1].x - abc[0].x;
    float y = abc[1].y - abc[0].y;
    float z = abc[1].z - abc[0].z;
    return new PVector(x, y, z);
  }

  public PVector getVecAC() {
    float x = abc[2].x - abc[0].x;
    float y = abc[2].y - abc[0].y;
    float z = abc[2].z - abc[0].z;
    return new PVector(x, y, z);
  }

  public PVector getVecBC() {
    float x = abc[2].x - abc[1].x;
    float y = abc[2].y - abc[1].y;
    float z = abc[2].z - abc[1].z;
    return new PVector(x, y, z);
  }

  public PVector getVecBA() {
    float x = abc[0].x - abc[1].x;
    float y = abc[0].y - abc[1].y;
    float z = abc[0].z - abc[1].z;
    return new PVector(x, y, z);
  }

  public PVector getVecCA() {
    float x = abc[0].x - abc[2].x;
    float y = abc[0].y - abc[2].y;
    float z = abc[0].z - abc[2].z;
    return new PVector(x, y, z);
  }

  public Point getVertA() {
    return abc[0];
  }

  public Point getVertB() {
    return abc[1];
  }

  public Point getVertC() {
    return abc[2];
  }

  public Hit isHit(Ray ray) {
    float rayNormalDot = a * ray.dir.x + b * ray.dir.y + c * ray.dir.z;
    
    t = -(a * ray.origin.x + b * ray.origin.y + c * ray.origin.z + d);
    
    //avoid divide by zero
    t = rayNormalDot == 0 ? -1 : t / rayNormalDot;
    if (!isIntersect(ray)) {
      return null;
    }
    //t = Math.abs(t);
    Point p = getHitPoint(ray, t);

    if (isInTriangle(p)) {
      Hit hit = null;
      if (debug_flag) {
        println("side 1, 2, 3: ");
      }
      hit = new Hit(material, p, normal, ray, t);
      hit.objectId = id;
      return hit;
    }
    return null;
  }

  private boolean isIntersect(Ray ray) {
    //t < 0 always wrong, 0 < t < 1 shadow/eye ray, t > 1 eye ray only
    if (ray.shadowRay) {
      return t > epsilon && t < 1;
    }
    return t > epsilon;
  }
  
  private boolean isInTriangle(Point p) {
    //half plane test
    Point vertA = getVertA();
    Point vertB = getVertB();
    Point vertC = getVertC();
    
    PVector ap = new PVector(p.x - vertA.x, p.y - vertA.y, 
                             p.z - vertA.z);
    PVector ab = new PVector(vertB.x - vertA.x, vertB.y - vertA.y, 
                             vertB.z - vertA.z);
    float side1 = side(ap, ab, normal);

    PVector bp = new PVector(p.x - vertB.x, p.y - vertB.y, 
                             p.z - vertB.z);
    PVector bc = new PVector(vertC.x - vertB.x, vertC.y - vertB.y, 
                             vertC.z - vertB.z);
    float side2 = side(bp, bc, normal);

    PVector cp = new PVector(p.x - vertC.x, p.y - vertC.y, 
                             p.z - vertC.z);
    PVector ca = new PVector(vertA.x - vertC.x, vertA.y - vertC.y, 
                             vertA.z - vertC.z);
    float side3 = side(cp, ca, normal);
    //if (debug_flag && ray.shadowRay) {
    //  println("side 1, 2, 3: ", p, side1, side2, side3);
    //}
    if (side1 >= 0 && side2 >= 0 && side3 >= 0 || 
        side1 <= 0 && side2 <= 0 && side3 <= 0) {
      return true;
    }
    return false;
  }

  private float side(PVector ap, PVector ab, PVector normal) {
    
    PVector cross = ap.cross(ab);
    //cross.normalize();
    float dot = normal.dot(cross);
    return dot;
  }
  
  public void setMaterial(Material material) {
    this.material = material;
  }
}

class Sphere  extends SceneObject implements HitTest {
  public Point center;
  public float radius;
  
  Sphere(Point center, float radius) {
    this.center = center;
    this.radius = radius;
  }
  
  
  public Hit isHit(Ray ray) {
    float t = nearestIntersection(ray.origin, ray.dir);
    if (t < 0) {
      return null;
    }
    
    Point p = getHitPoint(ray, t);
    //PVector normal = new PVector(p.x - (center.x + ray.motionOffset.x), 
    //                             p.y - (center.y + ray.motionOffset.y), 
    //                             p.z - (center.z + ray.motionOffset.z));
    PVector normal = new PVector(p.x - (center.x), 
                                 p.y - (center.y), 
                                 p.z - (center.z));                            
    normal.normalize();
    
    Hit hit = new Hit(material, p, normal, ray, t);
    hit.objectId = id;
    return hit;
  }
  
  public Point center(){
    return center;
  }
  
  private float nearestIntersection(Point o, PVector d) {
    float a = d.x * d.x + d.y * d.y + d.z * d.z;
    float ox = o.x - center.x;
    float oy = o.y - center.y;
    float oz = o.z - center.z;
    float b = 2 * (ox * d.x + oy * d.y + oz * d.z);
    float c = ox * ox + oy * oy + oz * oz - radius * radius;
    float discriminant = b * b - 4 * a * c;
    if (discriminant < 0) {
      return -1;
    }
    
    float t1 = (float)(-b + Math.sqrt(discriminant)) / (2 * a);
    float t2 = (float)(-b - Math.sqrt(discriminant)) / (2 * a);
    
    return t1 <= t2 ? t1 : t2;
  }
  
}
