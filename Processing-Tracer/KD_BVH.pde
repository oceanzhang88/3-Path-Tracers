enum Axis {
  X, Y, Z
}

class SplitPoint {
  public float[] min3;
  public float[] max3;
  public Axis axis;
  public int breakPoint;
  
  SplitPoint(float[] min3, float[] max3, Axis axis, int breakPoint) {
    this.min3 = min3;
    this.max3 = max3;
    this.axis = axis;
    this.breakPoint = breakPoint;
  }
}

class BVHNode {
  public BBox bbox;
  public BVHNode left;
  public BVHNode right;
  public int l, r;
  
  private Hit traverse(Ray ray, ArrayList<Triangle> triangles) {
    //if (debug_flag) {
    //  println("debug bvh tree traversal!");
    //}
    Hit hit = bbox.isHit(ray);
    if (hit == null) {
      return null;
    }
    
    //leaf node, linear search with triangles
    if (left == null && right == null) {
      Hit nearestHit = null;
      float minDist = Float.MAX_VALUE;
      for (int i = l; i < r; i++) {
        HitTest tri = triangles.get(i);
        Hit curT = tri.isHit(ray);
        if (curT == null) {
          continue;
        }
        if (curT.t > 0 && curT.t < minDist) {
          minDist = curT.t;
          nearestHit = curT;
        }
      }
      return nearestHit;
    }
    
    Hit t1 = left.traverse(ray, triangles);
    Hit t2 = right.traverse(ray, triangles);
    if (t1 == null) {
      return t2;
    }
    if (t2 == null) {
      return t1;
    }
    
    return t1.t < t2.t ? t1 : t2;
  }
}

class BVH extends SceneObject implements HitTest {
  private BVHNode root;
  private ArrayList<Triangle> triangles;
  private int leafSize;
  private int depth;
  
  BVH (int leafSize) {
    this.leafSize = leafSize;
    this.triangles = new ArrayList<Triangle>();
  } 
  
  public void build () {
    this.root = buildRec1(0, triangles.size(), 1);
    println("BVH Tree Depth: ", depth);
  }
  
  public Point center(){
    return null;
  }
  
  public void addTriangle (Triangle tri) {
    triangles.add(tri);
  }
  
  
  private BVHNode buildRec1(int l, int r, int depth) {
    //println("Current BVH Depth: ", depth);
    BVHNode node = new BVHNode();
    node.l = l;
    node.r = r;
    
    SplitPoint sp = findSplitPoint1(l, r);
    node.bbox = new BBox(blackMat, sp.min3, sp.max3, false);
     
    //return leaf node
    if (r - l <= leafSize) {
      this.depth = depth;
      node.left = null;
      node.right = null;
      return node;
    } 
    rangesort(sp.axis.ordinal(), l, r);
   
    int mid = (l + r) / 2;
    node.left = buildRec1(l, mid, depth + 1);
    node.right = buildRec1(mid, r, depth + 1);
      
    return node;
  }
  
  private SplitPoint findSplitPoint1(int l, int r) {
    float minx = Float.MAX_VALUE;
    float maxx = -Float.MAX_VALUE;
    float miny = Float.MAX_VALUE;
    float maxy = -Float.MAX_VALUE;
    float minz = Float.MAX_VALUE;
    float maxz = -Float.MAX_VALUE;
     
    for (int i = l; i < r; i++) {
      Triangle tri = triangles.get(i);
      
      for (int j = 0; j < 3; j++) {
        Point p = tri.abc[j];
        minx = Math.min(minx, p.x);
        miny = Math.min(miny, p.y);
        minz = Math.min(minz, p.z);
        
        maxx = Math.max(maxx, p.x);
        maxy = Math.max(maxy, p.y);
        maxz = Math.max(maxz, p.z);
      }
    }
    
    float dx = Math.abs(maxx - minx);
    float dy = Math.abs(maxy - miny);
    float dz = Math.abs(maxz - minz);
    Axis axis = Axis.X;
    
    if(dx > dy && dx > dz) {
      axis = Axis.X;
    }
    
    if(dy > dx && dy > dz) {
      axis =  Axis.Y;
    }
    
    if(dz > dx && dz > dy) {
      axis = Axis.Z;
    }
    
    float[] min3 = new float[]{minx, miny, minz};
    float[] max3 = new float[]{maxx, maxy, maxz};
    SplitPoint sp = new SplitPoint(min3, max3, axis, -1);
    return sp;
  }
  
  private void rangesort(int ax, int l, int r) {
    switch (ax) {
        case 0:
          Collections.sort(triangles.subList(l, r), tricmpX);
          break;
        case 1:
          Collections.sort(triangles.subList(l, r), tricmpY);
          break;
        case 2:
          Collections.sort(triangles.subList(l, r), tricmpZ);
          break;
      }
  }

  public Hit isHit(Ray ray) {
    Hit node = root.traverse(ray, triangles);
    return node;
  }
}
