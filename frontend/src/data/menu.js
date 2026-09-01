// ---------------------------------------------------------------------------
// Barni Coffee — static catalogue data (front-end only).
// When the Django backend lands, replace these arrays with API responses from
// e.g. `/api/menu/foods/` and `/api/menu/drinks/`.
// ---------------------------------------------------------------------------

export const FOOD_TYPES = [
  { id: 'all', label: 'All', icon: '🍽️' },
  { id: 'main', label: 'Main Course', icon: '🥩' },
  { id: 'appetizer', label: 'Appetizer', icon: '🍟' },
  { id: 'salad', label: 'Salad', icon: '🥗' },
  { id: 'snack', label: 'Snack', icon: '🥪' },
]

export const DRINK_TYPES = [
  { id: 'all', label: 'All', icon: '☕' },
  { id: 'hot', label: 'Hot Drinks', icon: '☕' },
  { id: 'cold', label: 'Cold Drinks', icon: '🧊' },
]

export const FOODS = [
  { id: 'p1', name: 'French Fries', price: 50, emoji: '🍟', type: 'appetizer' },
  { id: 'p2', name: 'Burger', price: 200, emoji: '🍔', type: 'main' },
  { id: 'p3', name: 'Grilled Chicken', price: 250, emoji: '🍗', type: 'main' },
  { id: 'p4', name: 'Pasta Alfredo', price: 180, emoji: '🍝', type: 'main' },
  { id: 'p5', name: 'Club Sandwich', price: 140, emoji: '🥪', type: 'snack' },
  { id: 'p6', name: 'Caesar Salad', price: 110, emoji: '🥗', type: 'salad' },
  { id: 'p7', name: 'Margherita Pizza', price: 220, emoji: '🍕', type: 'main' },
  { id: 'p8', name: 'Beef Steak', price: 320, emoji: '🥩', type: 'main' },
  { id: 'p9', name: 'Sushi Roll', price: 260, emoji: '🍣', type: 'main' },
  { id: 'p10', name: 'Veggie Wrap', price: 100, emoji: '🌯', type: 'snack' },
]

export const DRINKS = [
  { id: 'p11', name: 'Espresso', price: 60, emoji: '☕', type: 'hot' },
  { id: 'p12', name: 'Cappuccino', price: 80, emoji: '🥛', type: 'hot' },
  { id: 'p13', name: 'Fresh Juice', price: 90, emoji: '🥤', type: 'cold' },
  { id: 'p14', name: 'Mojito', price: 120, emoji: '🍹', type: 'cold' },
  { id: 'p15', name: 'Iced Tea', price: 70, emoji: '🧋', type: 'cold' },
  { id: 'p16', name: 'Hot Chocolate', price: 85, emoji: '🍫', type: 'hot' },
]

export const MENU = [...FOODS, ...DRINKS]

export const SIDES = ['With Egg', 'Without Egg', 'Plain']

export const ALL_TABLES = Array.from({ length: 15 }, (_, i) => i + 1)

export const PAY_METHODS = ['Chapa', 'CBE', 'BOA', 'Telebirr', 'Awash']

export const PAY_ACCOUNTS = {
  CBE: {
    bank: 'Commercial Bank of Ethiopia (CBE)',
    accountNumber: '1000234567890',
    accountName: 'Barni Coffee PLC',
    pattern: /^1000\d{9}$/,
    hint: 'CBE account must start with 1000 and be 13 digits',
  },
  BOA: {
    bank: 'Bank of Abyssinia (BOA)',
    accountNumber: '4520123456789012',
    accountName: 'Barni Coffee PLC',
    pattern: /^4520\d{12}$/,
    hint: 'BOA account must start with 4520 and be 16 digits',
  },
  Telebirr: {
    bank: 'Telebirr',
    accountNumber: '+251911000000',
    accountName: 'Barni Coffee PLC',
    pattern: /^\+2519\d{8}$/,
    hint: 'Telebirr must be +2519 followed by 8 digits',
  },
  Awash: {
    bank: 'Awash Bank',
    accountNumber: '017012345678901',
    accountName: 'Barni Coffee PLC',
    pattern: /^0170\d{11}$/,
    hint: 'Awash account must start with 0170 and be 15 digits',
  },
}

export const RESTAURANT_ACCOUNT = PAY_ACCOUNTS.CBE

export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
export const PHONE_REGEX = /^\+?\d{10,15}$/

export const INGREDIENTS = {
  p1: { raw: [{ n: 'Potato', a: '300g' }], processed: [{ n: 'Cooking Oil', a: '50ml' }, { n: 'Salt', a: '5g' }] },
  p2: { raw: [{ n: 'Beef Patty', a: '150g' }, { n: 'Bun', a: '1 pc' }], processed: [{ n: 'Cheese Slice', a: '1 pc' }, { n: 'Ketchup', a: '10ml' }] },
  p3: { raw: [{ n: 'Chicken Thigh', a: '250g' }], processed: [{ n: 'Spice Mix', a: '8g' }, { n: 'Butter', a: '10g' }] },
  p4: { raw: [{ n: 'Pasta', a: '180g' }], processed: [{ n: 'Cream Sauce', a: '80ml' }, { n: 'Parmesan', a: '15g' }] },
  p5: { raw: [{ n: 'Bread Slice', a: '3 pc' }, { n: 'Chicken Breast', a: '100g' }], processed: [{ n: 'Mayonnaise', a: '12ml' }] },
  p6: { raw: [{ n: 'Lettuce', a: '120g' }], processed: [{ n: 'Caesar Dressing', a: '25ml' }, { n: 'Croutons', a: '20g' }] },
  p7: { raw: [{ n: 'Pizza Dough', a: '220g' }, { n: 'Tomato', a: '80g' }], processed: [{ n: 'Mozzarella', a: '90g' }] },
  p8: { raw: [{ n: 'Beef Steak Cut', a: '280g' }], processed: [{ n: 'Black Pepper Sauce', a: '40ml' }] },
  p9: { raw: [{ n: 'Rice', a: '150g' }, { n: 'Nori Sheet', a: '2 pc' }], processed: [{ n: 'Soy Sauce', a: '10ml' }] },
  p10: { raw: [{ n: 'Tortilla Wrap', a: '1 pc' }, { n: 'Mixed Veg', a: '120g' }], processed: [{ n: 'Hummus', a: '20g' }] },
  p11: { raw: [{ n: 'Coffee Beans', a: '18g' }], processed: [{ n: 'Water', a: '30ml' }] },
  p12: { raw: [{ n: 'Coffee Beans', a: '18g' }], processed: [{ n: 'Steamed Milk', a: '150ml' }] },
  p13: { raw: [{ n: 'Fresh Fruit', a: '250g' }], processed: [{ n: 'Sugar Syrup', a: '10ml' }] },
  p14: { raw: [{ n: 'Mint Leaves', a: '6 pc' }, { n: 'Lime', a: '1 pc' }], processed: [{ n: 'Soda Water', a: '120ml' }] },
  p15: { raw: [{ n: 'Tea Leaves', a: '5g' }], processed: [{ n: 'Ice', a: '100g' }, { n: 'Sugar Syrup', a: '10ml' }] },
  p16: { raw: [{ n: 'Cocoa Powder', a: '20g' }], processed: [{ n: 'Steamed Milk', a: '180ml' }] },
}
